"""Evidence tests: check a candidate cause against the data. All numbers come from SQL run through
data_access (read-only, logged). Each test returns its numbers, the SQL it ran, and a deterministic
reading: SUPPORTS / WEAKENS / INCONCLUSIVE.

Expected tables (built in Phase 0 as Trino views; synthetic copies in demo/data):
  agg_weekly_issuer_merchant(week_start, issuer_bank, card_id, merchant_id, category, spend, txns, cards)
  txn_weekly_card_merchant(week_start, card_key, issuer_bank, card_id, merchant_id, category, spend)
     card_key is a salted hash made inside Trino; it never leaves the query (results are aggregates).
SQL is standard and runs unchanged on Trino and DuckDB.
"""
from __future__ import annotations

import datetime as dt

T_WEEKLY = "agg_weekly_issuer_merchant"
T_CARD = "txn_weekly_card_merchant"


def _q(s):
    return "'" + str(s).replace("'", "''") + "'"


def _weeks(week_start: str, baseline_weeks: int):
    wk = dt.date.fromisoformat(week_start)
    return wk - dt.timedelta(weeks=baseline_weeks), wk - dt.timedelta(days=1), wk, wk + dt.timedelta(days=6)


def switching(src, flag, competitor_id, baseline_weeks=8):
    """Did the cardholders who used merchant A before the dip move their spend to merchant B?"""
    b0, b1, w0, w1 = _weeks(flag["week_start"], baseline_weeks)
    sql = f"""
WITH cohort AS (
  SELECT DISTINCT card_key FROM {T_CARD}
  WHERE issuer_bank = {_q(flag['issuer_bank'])} AND merchant_id = {_q(flag['merchant_id'])}
    AND week_start BETWEEN DATE '{b0}' AND DATE '{b1}' AND spend > 0)
SELECT t.merchant_id,
       SUM(CASE WHEN t.week_start BETWEEN DATE '{b0}' AND DATE '{b1}' THEN t.spend ELSE 0 END) / {baseline_weeks} AS base_weekly,
       SUM(CASE WHEN t.week_start BETWEEN DATE '{w0}' AND DATE '{w1}' THEN t.spend ELSE 0 END) AS flag_week,
       COUNT(DISTINCT t.card_key) AS cohort_cards
FROM {T_CARD} t JOIN cohort c ON t.card_key = c.card_key
WHERE t.merchant_id IN ({_q(flag['merchant_id'])}, {_q(competitor_id)})
  AND t.week_start BETWEEN DATE '{b0}' AND DATE '{w1}'
GROUP BY t.merchant_id"""
    df = src.run_sql(sql, purpose=f"switching {flag['flag_id']}").set_index("merchant_id")
    a, b = flag["merchant_id"], competitor_id
    if a not in df.index:
        return _res("SWITCHING", sql, {}, "INCONCLUSIVE", "No cohort spend found at the flagged merchant.")
    lost = float(df.loc[a, "base_weekly"] - df.loc[a, "flag_week"])
    gained = float(df.loc[b, "flag_week"] - df.loc[b, "base_weekly"]) if b in df.index else 0.0
    recapture = gained / lost if lost > 0 else 0.0
    nums = {"cohort_cards": int(df.loc[a, "cohort_cards"]), "cohort_lost_spend_at_flagged": round(lost, 2),
            "cohort_gained_spend_at_competitor": round(gained, 2), "recapture_share": round(recapture, 3)}
    reading = "SUPPORTS" if recapture >= 0.3 else ("WEAKENS" if recapture < 0.1 else "INCONCLUSIVE")
    return _res("SWITCHING", sql, nums, reading,
                f"{recapture:.0%} of the spend the flagged merchant's regular cardholders stopped spending there "
                f"reappeared at the competitor in the same week.")


def eligibility_did(src, flag, offer_issuer: str | None, baseline_weeks=8):
    """Did the dip happen only on cards that had the competitor offer (difference-in-differences)?"""
    b0, b1, w0, w1 = _weeks(flag["week_start"], baseline_weeks)
    sql = f"""
SELECT issuer_bank,
       SUM(CASE WHEN week_start BETWEEN DATE '{b0}' AND DATE '{b1}' THEN spend ELSE 0 END) / {baseline_weeks} AS base_weekly,
       SUM(CASE WHEN week_start BETWEEN DATE '{w0}' AND DATE '{w1}' THEN spend ELSE 0 END) AS flag_week
FROM {T_WEEKLY}
WHERE merchant_id = {_q(flag['merchant_id'])} AND week_start BETWEEN DATE '{b0}' AND DATE '{w1}'
GROUP BY issuer_bank"""
    df = src.run_sql(sql, purpose=f"did {flag['flag_id']}")
    df["chg"] = df["flag_week"] / df["base_weekly"] - 1
    treated_name = offer_issuer or flag["issuer_bank"]
    is_t = df["issuer_bank"].str.lower().apply(lambda s: treated_name.lower() in s or s in treated_name.lower())
    if not is_t.any() or is_t.all():
        return _res("ELIGIBILITY_DID", sql, {}, "INCONCLUSIVE", "No untreated comparison group in the data.")
    t = df[is_t]
    c = df[~is_t]
    t_chg = float(t.flag_week.sum() / t.base_weekly.sum() - 1)
    c_chg = float(c.flag_week.sum() / c.base_weekly.sum() - 1)
    did = t_chg - c_chg
    nums = {"treated_group": treated_name, "treated_change": round(t_chg, 4),
            "control_groups": sorted(c.issuer_bank.tolist()), "control_change": round(c_chg, 4),
            "difference_in_differences": round(did, 4)}
    signed = did if flag["direction"] == "DROP" else -did
    reading = "SUPPORTS" if signed <= -0.05 else ("WEAKENS" if abs(did) < 0.02 or signed > 0 else "INCONCLUSIVE")
    return _res("ELIGIBILITY_DID", sql, nums, reading,
                f"Spend at the merchant changed {t_chg:+.1%} for {treated_name} cards versus {c_chg:+.1%} for other issuers.")


def category_total(src, flag, category: str, baseline_weeks=8):
    """Did the issuer's whole category fall (market move) or hold steady (substitution)?"""
    b0, b1, w0, w1 = _weeks(flag["week_start"], baseline_weeks)
    sql = f"""
SELECT SUM(CASE WHEN week_start BETWEEN DATE '{b0}' AND DATE '{b1}' THEN spend ELSE 0 END) / {baseline_weeks} AS base_weekly,
       SUM(CASE WHEN week_start BETWEEN DATE '{w0}' AND DATE '{w1}' THEN spend ELSE 0 END) AS flag_week
FROM {T_WEEKLY}
WHERE issuer_bank = {_q(flag['issuer_bank'])} AND category = {_q(category)}
  AND week_start BETWEEN DATE '{b0}' AND DATE '{w1}'"""
    r = src.run_sql(sql, purpose=f"category {flag['flag_id']}").iloc[0]
    chg = float(r.flag_week / r.base_weekly - 1) if r.base_weekly else 0.0
    within = abs(chg) < 0.05
    if flag["direction"] == "DROP":
        reading = "SUPPORTS" if chg > -0.05 else "WEAKENS"
        tail = "spend moved within the category." if within or chg > 0 else "the whole category fell."
    else:  # for a rise this test describes the effect (shifted vs new spend); it neither supports nor weakens
        reading = "INFO"
        tail = "the rise was mostly taken from other merchants in the category." if within else "the category grew too (new spend)."
    return _res("CATEGORY_TOTAL", sql, {"category": category, "category_change": round(chg, 4)}, reading,
                f"The issuer's total {category.replace('_', ' ').lower()} spend changed {chg:+.1%}: " + tail)


def _res(test, sql, numbers, reading, text):
    return {"test": test, "reading": reading, "numbers": numbers, "plain_english": text, "sql": sql.strip()}


def confidence(tests: list[dict]) -> str:
    """HIGH: three supporting tests. MEDIUM: all decisive tests support (at least one). LOW otherwise."""
    sup = sum(t["reading"] == "SUPPORTS" for t in tests)
    weak = sum(t["reading"] == "WEAKENS" for t in tests)
    if weak or sup == 0:
        return "LOW"
    return "HIGH" if sup >= 3 else "MEDIUM"
