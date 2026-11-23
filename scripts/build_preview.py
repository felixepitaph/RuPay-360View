"""Build app/platform_preview.html: a single-file, interactive preview of RuPay 360.

Provenance, shown on every panel of the page:
  REAL       card, offer and event catalogs; page-vs-MITC conflicts; reward rates parsed from the catalogs
  ENGINE     Deal Model (engine/js/deal_engine.js, parity-tested against Python); insight findings
  SYNTHETIC  all spend, card counts, cohorts, wallet share, offer-effect library (seeded, made up)

Run from the repo root:
    PowerShell:  $env:PYTHONPATH="engine"; python scripts/build_preview.py
    bash:        PYTHONPATH=engine python scripts/build_preview.py
Then open app/platform_preview.html in a browser (works offline; fonts fall back to system fonts).
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "app" / "platform_preview.html"
TEMPLATE = ROOT / "scripts" / "platform_template.html"
ENGINE_JS = ROOT / "engine" / "js" / "deal_engine.js"
DEMO = ROOT / "demo" / "data"
LEDGER = ROOT / "runs" / "demo_ledger" / "findings.jsonl"
FOCUS_WEEK = "2027-01-04"
ISSUERS = ["YES BANK", "IDFC FIRST Bank"]
RNG = random.Random(360)


def jload(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- demo data + engine findings
def ensure_demo():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "engine")}
    if not (DEMO / "agg_weekly_issuer_merchant.parquet").exists():
        subprocess.run([sys.executable, str(ROOT / "demo" / "make_synthetic.py")], check=True, cwd=ROOT, env=env)
    if not LEDGER.exists():
        env.update(R360_SOURCE="local:demo/data", R360_QUERY_LOG="runs/query_log.jsonl")
        subprocess.run([sys.executable, "-m", "r360", "--ledger", "runs/demo_ledger", "run-insights",
                        "--week", FOCUS_WEEK], check=True, cwd=ROOT, env=env)


def telemetry():
    import duckdb
    con = duckdb.connect()
    agg = (DEMO / "agg_weekly_issuer_merchant.parquet").as_posix()
    txn = (DEMO / "txn_weekly_card_merchant.parquet").as_posix()
    rows = con.execute(f"select cast(week_start as varchar), issuer_bank, merchant_id, category, sum(spend), sum(txns), sum(cards) "
                       f"from '{agg}' group by 1,2,3,4 order by 1").fetchall()
    weeks = sorted({r[0] for r in rows})
    series = {}
    for w, i, m, c, s, t, n in rows:
        d = series.setdefault(f"{i}|{m}", {"issuer": i, "merchant": m, "category": c, "spend": [0.0] * len(weeks),
                                            "txns": [0] * len(weeks), "cards": [0] * len(weeks)})
        k = weeks.index(w)
        d["spend"][k], d["txns"][k], d["cards"][k] = round(s, 2), int(t), int(n)
    co = con.execute(f"""with u as (select distinct card_key, merchant_id from '{txn}' where spend>0)
        select a.merchant_id, b.merchant_id, count(*) n from u a join u b on a.card_key=b.card_key and a.merchant_id<b.merchant_id group by 1,2""").fetchall()
    users = dict(con.execute(f"select merchant_id, count(distinct card_key) from '{txn}' where spend>0 group by 1").fetchall())
    edges = [{"a": a, "b": b, "w": round(n / min(users[a], users[b]), 3)} for a, b, n in co]
    return {"weeks": weeks, "series": list(series.values()), "edges": edges, "merchant_users": users}


def findings():
    out = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        f = json.loads(line)
        best = f.get("best_explanation")
        out.append({"id": f["finding_id"], "status": f["status"], "issuer": f["flag"]["issuer_bank"], "merchant_id": f["flag"]["merchant_id"],
                    "merchant": f["merchant"]["name"], "category": f["merchant"]["category"], "week": f["flag"]["week_start"],
                    "z": f["flag"]["robust_z"], "pct": f["flag"]["pct_change"], "actual": f["flag"]["actual_spend"], "expected": f["flag"]["expected_spend"],
                    "headline": f["headline"], "confidence": best["confidence"] if best else None, "best": best,
                    "critic": f.get("critic_checks") or [],
                    "candidates": [{"summary": c["summary"], "type": c["type"], "prior_score": c["prior_score"], "components": c.get("components"),
                                    "competitor": c.get("competitor_merchant_id"),
                                    "tests": [{k: t.get(k) for k in ("test", "reading", "plain_english", "sql", "numbers")} for t in c["tests"]]}
                                   for c in f["candidates"]]})
    out.sort(key=lambda f: -abs(f["pct"]))
    return out


# ---------------------------------------------------------------- catalogs (real)
BUCKETS = [["online", "Online shopping"], ["offline", "In-store (POS)"], ["dining_travel", "Dining and travel"],
           ["grocery_utility", "Groceries and utilities"], ["fuel", "Fuel"], ["upi", "UPI on credit"]]
KEYS = {"online": ["online"], "offline": ["offline", "pos ", "pos transactions", "in-store", "retail"],
        "dining_travel": ["dining", "travel", "hotel", "flight", "international"],
        "grocery_utility": ["grocery", "utilit", "insurance", "bill"], "fuel": ["fuel", "hpcl"], "upi": ["upi"]}


def _head(cat):
    """Category text before any exclusion clause, lower-case."""
    return re.split(r"\bexcept|\bexcl|\(excl|\bnot on", cat.lower())[0] + " "


def parse_rates(card):
    """Effective reward % per spend bucket, parsed from the page's earn rules (first matching rule wins, then a catch-all)."""
    rc = card.get("reward_currency") if isinstance(card.get("reward_currency"), dict) else {}
    pv, pv_assumed = rc.get("point_value_inr"), False
    is_cash = (rc.get("type") or "").lower() == "cashback" or "cashback" in (rc.get("name") or "").lower()
    if pv is None and not is_cash:
        pv, pv_assumed = 0.25, True
    rules = []
    for e in card.get("earn_rules") or []:
        cat, txt, pct = e.get("category") or "", e.get("rate_text") or "", None
        if e.get("cashback_pct") is not None:
            pct = float(e["cashback_pct"])
        elif e.get("points_per_block") and e.get("block_inr") and pv:
            mult = 1.0
            m = re.search(r"(\d+(?:\.\d+)?)\s*[xX]\b", txt)
            if m and e["points_per_block"] == 1:
                mult = float(m.group(1))
            pct = e["points_per_block"] * mult / e["block_inr"] * pv * 100
        elif "no points" in txt.lower() or "no reward" in txt.lower():
            pct = 0.0
        rules.append({"cat": cat, "text": txt, "pct": None if pct is None else round(pct, 3), "cap": e.get("cap_text"), "points": pct is not None and not e.get("cashback_pct")})
    rates, src = {}, {}
    for b, _ in BUCKETS:
        for r in rules:
            if r["pct"] is not None and any(k in _head(r["cat"]) for k in KEYS[b]):
                rates[b], src[b] = r["pct"], r["cat"]
                break
    generic = next((r for r in rules if r["pct"] is not None and (_head(r["cat"]).startswith(("all", "other eligible", "everything"))
                                                                   or r["cat"].strip().lower() == "spends")), None)
    for b, _ in BUCKETS:
        if b not in rates and b != "upi" and generic:
            rates[b], src[b] = generic["pct"], generic["cat"] + " (catch-all)"
    return {"rates": rates, "src": src, "rules": rules, "point_value": pv, "pv_assumed": pv_assumed, "cashback": is_cash}


def catalogs():
    cards, notyet = [], {}
    for issuer, path in (("YES BANK", "catalog/yes_bank/cvp_yes_2026-11-23.json"), ("IDFC FIRST Bank", "catalog/idfc_first/cvp_idfc_2026-11-23.json")):
        d = jload(path)
        notyet[issuer] = d.get("not_yet_extracted", [])
        for c in d["cards"]:
            fees, lg, fx = c.get("fees") or {}, c.get("lounge") or {}, c.get("forex") or {}
            cards.append({"id": c["card_id"], "name": c["card_name"], "issuer": issuer, "network": c.get("network"), "backing": c.get("backing"),
                          "joining": fees.get("joining_inr"), "annual": fees.get("annual_inr"), "waiver": fees.get("annual_waiver_spend_inr"),
                          "forex": fx.get("markup_text"), "lounge_dom": lg.get("domestic"), "lounge_int": lg.get("international"),
                          "fuel": c.get("fuel_surcharge_waiver"), "milestones": c.get("milestones") if isinstance(c.get("milestones"), list) else [],
                          "welcome": c.get("welcome_benefits") if isinstance(c.get("welcome_benefits"), list) else [],
                          "eligibility": c.get("eligibility") or {}, "verified": c.get("verification_status"),
                          "conflicts": c.get("page_conflicts") or [], "source": (c.get("source") or {}).get("url", ""), **parse_rates(c)})
    offers = []
    for issuer, path in (("IDFC FIRST Bank", "catalog/idfc_first/offers_idfc_nov2026_booklet.json"), ("YES BANK", "catalog/yes_bank/offers_yes_credit_live_2026-11-23.json")):
        for o in jload(path):
            b, v = o.get("benefit") or {}, o.get("validity") or {}
            parts = []
            if b.get("rate_pct") is not None: parts.append(f"{b['rate_pct']:g}% off")
            if b.get("flat_inr") is not None: parts.append(f"₹{b['flat_inr']:,.0f} off")
            if b.get("min_txn_inr"): parts.append(f"on ₹{b['min_txn_inr']:,.0f}+")
            if b.get("max_inr"): parts.append(f"up to ₹{b['max_inr']:,.0f}")
            s = (o.get("sources") or [{}])[0]
            offers.append({"id": o["offer_id"], "issuer": issuer, "merchant": o.get("merchant_brand") or "", "category": o.get("category") or "",
                           "mode": o.get("payment_mode"), "channel": o.get("channel"), "benefit": " ".join(parts) or (b.get("type") or "").replace("_", " ").lower(),
                           "rate": b.get("rate_pct"), "flat": b.get("flat_inr"), "min": b.get("min_txn_inr"), "cap": b.get("max_inr"),
                           "cond": o.get("conditions") or "", "start": v.get("start_date"), "end": v.get("end_date"), "dow": v.get("days_of_week") or [],
                           "source": s.get("document") or "", "locator": s.get("locator") or "", "ncards": len(o.get("eligible_cards") or []),
                           "confidence": o.get("extraction_confidence")})
    ev = jload("catalog/events/proposition_events.json")
    ev = ev.get("events", ev) if isinstance(ev, dict) else ev
    events = [{"id": e["event_id"], "date": e["effective_date"], "issuer": e["issuer_bank"], "type": e["event_type"], "direction": e.get("direction"),
               "desc": e["description"], "cards": e.get("card_ids") or [], "cats": e.get("affected_categories") or [],
               "source": ((e.get("sources") or [{}])[0]).get("document", "")} for e in sorted(ev, key=lambda e: e["effective_date"])]
    return cards, offers, events, notyet


def conflicts():
    text = (ROOT / "docs" / "RECONCILIATION_2026-11-23.md").read_text(encoding="utf-8")
    sec = text.split("## Conflicts", 1)[1].split("\n## ", 1)[0]
    return [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in sec.splitlines()
            if ln.startswith("|") and not ln.startswith("|---") and not ln.startswith("| Card")]


# ---------------------------------------------------------------- synthetic (per-customer and library views)
def synthetic(cards):
    cats = ["Groceries and quick commerce", "Food delivery", "Online shopping", "Fuel", "Utilities and bills", "Travel", "Dining out", "Electronics (EMI)"]
    wallet = {}
    for iss, base in (("YES BANK", 0.31), ("IDFC FIRST Bank", 0.42)):
        rows = [{"cat": c, "card": round(max(0.05, min(0.85, base + RNG.uniform(-0.18, 0.22))), 3), "net_new": round(RNG.uniform(0.35, 0.7), 3),
                 "customers": RNG.randint(4000, 40000)} for c in cats]
        for r in rows:
            r["upi_savings"] = round(1 - r["card"], 3)
        trend, x = [], base - 0.05
        for _ in range(15):
            x = min(0.9, x + RNG.uniform(-0.004, 0.012)); trend.append(round(x, 4))
        wallet[iss] = {"cats": rows, "trend": trend}
    cohorts = []
    for c in cards:
        if c["id"] not in ("YES_MARQUEE", "YES_ACE", "YES_PROSPERITY_CASHBACK_PLUS", "IDFC_FIRST_MILLENNIA", "IDFC_FIRST_WOW", "IDFC_FIRST_WEALTH", "IDFC_HELLO_CASHBACK"):
            continue
        k, early, curve = RNG.uniform(0.010, 0.032), RNG.uniform(0.12, 0.30), [1.0]
        for d in range(1, 181):
            drop = (early / 30 if d <= 30 else 0) + k / 30 * (6 if d in (31, 61, 91) else 1)
            curve.append(max(0.05, curve[-1] * (1 - drop)))
        n = RNG.randint(1800, 9000)
        cohorts.append({"card": c["id"], "name": c["name"], "issuer": c["issuer"], "curve": [round(curve[d], 4) for d in range(0, 181, 5)], "n": n,
                        "first_txn_days": round(RNG.uniform(3, 19), 1), "welcome": (c["welcome"] or ["not stated"])[0][:110]})
    health = []
    for c in cards:
        v, tr, spark = RNG.uniform(80, 120), RNG.uniform(-2.2, 1.8), []
        for _ in range(12):
            v = max(20, v + tr + RNG.uniform(-3, 3)); spark.append(round(v, 1))
        breadth, velocity = round(RNG.uniform(2.1, 5.6), 2), round(spark[-1] / spark[0] - 1, 3)
        health.append({"card": c["id"], "name": c["name"], "issuer": c["issuer"], "spark": spark, "velocity": velocity, "breadth": breadth,
                       "rails": round(RNG.uniform(1.1, 2.6), 2), "at_risk": RNG.randint(120, 2600),
                       "score": max(0, min(100, round(60 + velocity * 120 + (breadth - 3.5) * 9 + RNG.uniform(-6, 6))))})
    bunch = {}
    for c in cards:
        if not c.get("waiver"):
            continue
        thr, sample = c["waiver"], []
        for _ in range(6000):
            x = math.exp(RNG.gauss(math.log(thr * 0.55), 0.75))
            if thr * 0.85 <= x < thr and RNG.random() < 0.42:
                x = thr * RNG.uniform(1.0, 1.06)
            sample.append(x)
        hi, nb = thr * 2.5, 50
        hist = [0] * nb
        for x in sample:
            if x < hi:
                hist[int(x / hi * nb)] += 1
        bunch[c["id"]] = {"thr": thr, "hi": hi, "hist": hist, "n": len(sample)}
    lib = []
    merchants = ["Zepto", "Blinkit", "Swiggy", "Zomato", "Amazon", "Flipkart", "Myntra", "Croma", "BigBasket", "EazyDiner", "MakeMyTrip", "Nykaa"]
    for _ in range(60):
        disc, days, mn, rep = RNG.choice([5, 7.5, 10, 10, 12.5, 15, 20, 25]), RNG.choice([3, 7, 7, 14, 30, 30]), RNG.choice([299, 499, 999, 1499, 2999, 4999]), RNG.choice([1, 1, 2, 3, 4])
        lift = (0.9 * disc ** 0.85 * (1 + 0.2 * math.log(7 / days + 1)) * (1 - 0.06 * math.log(mn / 299 + 1)) + RNG.gauss(0, 2.2)) * 0.82 ** (rep - 1)
        pull = min(0.7, max(0.05, 0.18 + 0.012 * disc + (0.15 if days <= 7 else 0) + RNG.gauss(0, 0.06)))
        lib.append({"merchant": RNG.choice(merchants), "disc": disc, "days": days, "min": mn, "lift": round(max(-2, lift), 2), "pull": round(pull, 3), "repeat": rep})
    return {"wallet": wallet, "cohorts": cohorts, "health": health, "bunch": bunch, "library": lib}


# ---------------------------------------------------------------- synthetic portfolio (monthly, three channels)
NM = 24
CHANNELS = ("CC", "UPI", "INTL")
SEASON = {12: 1.10, 1: 0.95, 2: 0.92, 3: 1.00, 4: 0.97, 5: 1.00, 6: 0.98, 7: 0.97, 8: 0.99, 9: 1.00, 10: 1.12, 11: 1.14}
PARAM = {
    "YES BANK": {"cif0": 420_000, "g": 0.014, "issue0": 9000, "lag": [0.34, 0.28, 0.15, 0.08, 0.05],
                 "CC": {"a0": .36, "a1": .40, "tpac": 9.4, "ats": 2150, "dec": .070},
                 "UPI": {"s0": .22, "s1": .44, "a0": .20, "a1": .31, "tpac": 13.0, "ats": 540, "dec": .105},
                 "INTL": {"s0": .30, "s1": .30, "a0": .065, "a1": .080, "tpac": 2.3, "ats": 8200, "dec": .115}},
    "IDFC FIRST Bank": {"cif0": 640_000, "g": 0.012, "issue0": 11000, "lag": [0.40, 0.27, 0.13, 0.07, 0.04],
                        "CC": {"a0": .43, "a1": .46, "tpac": 11.0, "ats": 1750, "dec": .062},
                        "UPI": {"s0": .26, "s1": .48, "a0": .22, "a1": .34, "tpac": 14.5, "ats": 480, "dec": .098},
                        "INTL": {"s0": .32, "s1": .32, "a0": .070, "a1": .090, "tpac": 2.6, "ats": 6900, "dec": .108}},
}
CODES = [("05", "Do not honor", "Issuer policy"), ("51", "Insufficient funds / over credit limit", "Cardholder"), ("55", "Incorrect PIN", "Cardholder"),
         ("54", "Expired card", "Cardholder"), ("61", "Exceeds amount limit", "Cardholder"), ("65", "Exceeds frequency limit", "Issuer policy"),
         ("57", "Transaction not permitted to cardholder", "Issuer policy"), ("62", "Restricted card", "Issuer policy"),
         ("82", "CVV / authentication validation failure", "Cardholder"), ("91", "Issuer or switch inoperative", "Technical"),
         ("96", "System malfunction", "Technical"), ("68", "Response received too late (timeout)", "Technical")]
CODE_P = {"CC": [.17, .27, .04, .02, .05, .04, .05, .02, .07, .09, .06, .12],
          "UPI": [.10, .22, .06, .01, .08, .06, .04, .02, .01, .14, .08, .18],
          "INTL": [.22, .20, .01, .03, .06, .03, .12, .03, .10, .06, .04, .10]}
MCC = [("5411 Grocery and supermarkets", .11, .8, .42), ("5499 Convenience and quick commerce", .05, .35, .22), ("5812 Restaurants", .07, .7, .30),
       ("5814 Fast food and delivery", .06, .3, .35), ("5541 Fuel stations", .07, .9, .28), ("4900 Utilities", .05, 1.3, .14), ("4814 Telecom", .03, .6, .16),
       ("4511 Airlines", .07, 4.5, .07), ("7011 Hotels", .05, 3.5, .05), ("4722 Travel agencies and OTAs", .06, 3.0, .08), ("5311 Department stores", .06, 1.5, .20),
       ("5651 Apparel", .06, 1.2, .18), ("5732 Electronics", .07, 5.0, .09), ("5912 Pharmacies", .03, .6, .15), ("5399 General merchandise", .09, 1.0, .38),
       ("8211 Education", .02, 3.0, .03), ("Other MCCs", .08, 1.0, .45)]
MCC_TILT = {"UPI": {"5499": 3, "5411": 1.6, "5814": 1.8, "5541": 1.5, "4900": 1.4, "4814": 2.0, "4511": .15, "7011": .1, "4722": .3, "5732": .3, "8211": .5},
            "INTL": {"4511": 4, "7011": 4, "4722": 2.5, "5812": 1.2, "5814": .5, "5411": .2, "5499": .02, "5541": .05, "4900": .05, "4814": .1, "5732": .6, "5399": 1.3}}
MERCH = {"CC": [("Amazon", .08, 1.0, .30), ("Flipkart", .06, 1.1, .22), ("Swiggy", .04, .25, .24), ("Zomato", .035, .25, .22), ("Myntra", .03, 1.3, .12), ("MakeMyTrip", .04, 3.5, .06),
                ("IRCTC", .025, 1.8, .10), ("Reliance Retail", .04, 1.1, .17), ("DMart", .03, 1.4, .14), ("Croma", .03, 5.0, .05), ("Nykaa", .02, 1.2, .08), ("BigBasket", .025, 1.3, .10),
                ("Apollo Pharmacy", .015, .7, .07), ("Indian Oil", .03, .9, .14), ("Uber", .02, .3, .12), ("Tata CLiQ", .012, 1.6, .04), ("Long tail (all others)", .36, 1.0, .62)],
         "UPI": [("Zepto", .08, .30, .22), ("Blinkit", .075, .30, .24), ("Swiggy", .06, .28, .20), ("Zomato", .05, .28, .18), ("BigBasket", .04, .8, .10), ("Reliance Retail", .05, 1.0, .14),
                 ("DMart", .04, 1.2, .10), ("Indian Oil", .05, .9, .15), ("Apollo Pharmacy", .02, .6, .07), ("Uber", .03, .35, .13), ("Amazon", .04, 1.0, .12), ("Flipkart", .025, 1.1, .08),
                 ("Airtel", .03, .8, .09), ("Jio", .03, .8, .09), ("Tata Power", .015, 1.4, .04), ("Long tail (all others)", .33, 1.0, .55)],
         "INTL": [("Booking.com", .07, 2.5, .08), ("Airbnb", .05, 2.0, .05), ("Emirates", .06, 4.0, .04), ("Singapore Airlines", .05, 4.0, .03), ("Uber", .03, .3, .10), ("Netflix", .02, .12, .12),
                  ("Apple Services", .03, .2, .15), ("Google Play", .02, .15, .14), ("Amazon", .05, 1.0, .10), ("Agoda", .04, 2.2, .05), ("Expedia", .03, 2.5, .04), ("Spotify", .01, .08, .06),
                  ("Duty free (Dubai)", .03, 1.8, .04), ("Marina Bay Sands", .02, 3.0, .02), ("Long tail (all others)", .39, 1.0, .55)]}
STATES = [("Maharashtra", .19), ("Karnataka", .13), ("Delhi NCR", .14), ("Tamil Nadu", .08), ("Telangana", .07), ("Gujarat", .06), ("West Bengal", .05), ("Uttar Pradesh", .07),
          ("Rajasthan", .03), ("Kerala", .03), ("Haryana", .04), ("Other states", .11)]
COUNTRIES = [("UAE", .22), ("USA", .17), ("Singapore", .10), ("United Kingdom", .10), ("Thailand", .07), ("Malaysia", .04), ("Germany", .03), ("France", .03), ("Saudi Arabia", .03), ("Other countries", .21)]
APPS = [("PhonePe", .31, 1.0, .46), ("Google Pay", .27, 1.0, .42), ("Paytm", .16, .9, .25), ("CRED", .08, 1.8, .14), ("BHIM", .05, .8, .09), ("Amazon Pay", .05, .9, .10), ("Navi", .02, .8, .04), ("Other apps", .06, .9, .10)]
PLANT_DRIFT = {("IDFC FIRST Bank", "UPI", "merchant", "Zepto"): 1.0, ("IDFC FIRST Bank", "UPI", "merchant", "Blinkit"): 0.6, ("YES BANK", "CC", "merchant", "Swiggy"): -0.8}
EVENTS = [{"i": 14, "issuer": "IDFC FIRST Bank", "label": "IDFC UPI activation push"}, {"i": 19, "issuer": "YES BANK", "label": "YES activation dip"},
          {"i": 17, "issuer": "YES BANK", "label": "YES international ticket uplift"}, {"i": 21, "issuer": "IDFC FIRST Bank", "label": "IDFC switch incidents"}]


def _ramp(i, a, b, i0=0, i1=NM - 1):
    return a + (b - a) * min(1, max(0, (i - i0) / max(1, (i1 - i0))))


def _dim(items, spend, txns, active, rng, plants, geo=False):
    n, w0 = len(items), [it[1] for it in items]
    tot0 = sum(w0)
    drifts = [plants.get(it[0], rng.uniform(-.30, .30)) for it in items]
    out = [{"k": it[0], "spend": [], "txns": [], "active": []} for it in items]
    for i in range(NM):
        w = [it[1] * math.exp(drifts[j] * i / (NM - 1) + rng.gauss(0, .035)) for j, it in enumerate(items)]
        s = sum(w)
        w = [x / s for x in w]
        sp = [spend[i] * x for x in w]
        raw = [sp[j] / items[j][2] for j in range(n)]
        k = txns[i] / sum(raw)
        for j in range(n):
            reach = (items[j][1] / tot0 * 1.15) if geo else items[j][3]
            out[j]["spend"].append(round(sp[j])); out[j]["txns"].append(round(raw[j] * k))
            out[j]["active"].append(round(active[i] * min(.97, reach * (1 + rng.gauss(0, .02)))))
    return out


def portfolio():
    r = random.Random(361)
    months = []
    for i in range(NM):
        mo, yr = (11 + i) % 12 + 1, 2024 + (11 + i) // 12
        months.append({"label": dt.date(yr, mo, 1).strftime("%b %y"), "m": mo})
    series, dims, dc, nu = {}, {}, {}, {}
    for iss, p in PARAM.items():
        S = {c: {k: [] for k in ("cif", "active", "issuance", "spend", "txns", "newusers", "declines", "decl_value")} for c in ("ALL",) + CHANNELS}
        cif_cc = [p["cif0"] * (1 + p["g"]) ** i for i in range(NM)]
        issuance = [p["issue0"] if i == 0 else (cif_cc[i] - cif_cc[i - 1]) + .004 * cif_cc[i - 1] for i in range(NM)]
        lag = p["lag"]
        new_all = [sum(lag[k] * issuance[max(0, i - k)] for k in range(len(lag))) for i in range(NM)]
        dc[iss] = {c: {code: [] for code, _, _ in CODES} for c in CHANNELS}
        for i in range(NM):
            season, row = SEASON[months[i]["m"]], {}
            for c in CHANNELS:
                q = p[c]
                if c == "CC":
                    cif = cif_cc[i]
                    act = _ramp(i, q["a0"], q["a1"]) - (0.032 * (1 - abs(i - 20) / 2.0) if iss == "YES BANK" and 19 <= i <= 21 else 0)
                    ats = q["ats"] * (1 + .004 * i)
                elif c == "UPI":
                    sh = _ramp(i, q["s0"], q["s1"] if iss != "IDFC FIRST Bank" else q["s0"] + .12, 0, NM - 1)
                    act = _ramp(i, q["a0"], q["a1"] if iss != "IDFC FIRST Bank" else q["a0"] + .05)
                    if iss == "IDFC FIRST Bank" and i >= 14:
                        sh += min(.10, .035 * (i - 13)); act += min(.07, .022 * (i - 13))
                    cif = cif_cc[i] * sh; ats = q["ats"] * (1 + .003 * i)
                else:
                    cif = cif_cc[i] * q["s0"]; act = _ramp(i, q["a0"], q["a1"]); ats = q["ats"] * (1 + .004 * i) * (1.18 if iss == "YES BANK" and i >= 17 else 1)
                act = max(.01, act * (1 + r.gauss(0, .012)) * (1 + (season - 1) * .15))
                active = cif * act
                tpac = q["tpac"] * season * (1 + r.gauss(0, .02))
                ats = ats * (1 + r.gauss(0, .015))
                txns = active * tpac; spend = txns * ats
                rate = q["dec"] * (1 + r.gauss(0, .04)) * (1 + (.35 if c == "UPI" and i > 12 else 0) * 0)
                p_codes = list(CODE_P[c])
                if iss == "IDFC FIRST Bank" and c == "CC" and i in (21, 22):
                    for j, (code, _, cls) in enumerate(CODES):
                        if cls == "Technical":
                            p_codes[j] *= 3.2
                    rate *= 1.35
                z = sum(p_codes); p_codes = [x / z for x in p_codes]
                declines = txns * rate / (1 - rate)
                for j, (code, _, _) in enumerate(CODES):
                    dc[iss][c][code].append(round(declines * p_codes[j] * (1 + r.gauss(0, .04))))
                share = {"CC": _ramp(i, .64, .52), "UPI": _ramp(i, .28, .40), "INTL": .08}
                if iss == "IDFC FIRST Bank" and i >= 14:
                    share["UPI"] += min(.08, .03 * (i - 13)); share["CC"] -= min(.08, .03 * (i - 13))
                row[c] = dict(cif=cif, active=active, spend=spend, txns=txns, declines=declines, decl_value=declines * ats * .9, newusers=new_all[i] * share[c],
                              issuance=issuance[i] * (1 if c == "CC" else (cif / cif_cc[i])))
            allrow = {k: sum(row[c][k] for c in CHANNELS) for k in ("spend", "txns", "declines", "decl_value")}
            allrow["cif"] = cif_cc[i]
            allrow["active"] = min(.95 * cif_cc[i], row["CC"]["active"] + .40 * row["UPI"]["active"] + .35 * row["INTL"]["active"])
            allrow["issuance"] = issuance[i]; allrow["newusers"] = new_all[i]
            row["ALL"] = allrow
            for c in ("ALL",) + CHANNELS:
                for k, v in row[c].items():
                    S[c][k].append(round(v))
        series[iss] = S
        # drill-down
        dims[iss] = {}
        for c in CHANNELS:
            sp, tx, ac = S[c]["spend"], S[c]["txns"], S[c]["active"]
            pl = lambda dim: {k[3]: v for k, v in PLANT_DRIFT.items() if k[0] == iss and k[1] == c and k[2] == dim}
            tilt = MCC_TILT.get(c, {})
            mcc = [(n, w * tilt.get(n[:4], 1), a, min(.97, rc * tilt.get(n[:4], 1) ** .5)) for n, w, a, rc in MCC]
            geo = [(n, w, 1.0, 0) for n, w in (COUNTRIES if c == "INTL" else STATES)]
            d = {"mcc": _dim(mcc, sp, tx, ac, r, pl("mcc")), "merchant": _dim(MERCH[c], sp, tx, ac, r, pl("merchant")), "geo": _dim(geo, sp, tx, ac, r, pl("geo"), geo=True)}
            if c == "UPI":
                d["app"] = _dim(APPS, sp, tx, ac, r, pl("app"))
            dims[iss][c] = d
        nu[iss] = {"lag": lag, "ttf": [round(_ramp(i, 15.5, 13.0 if iss == "IDFC FIRST Bank" else 14.5) + r.gauss(0, .4), 1) for i in range(NM)]}
    return {"months": [m["label"] for m in months], "mo_num": [m["m"] for m in months], "series": series, "dims": dims, "dc": dc, "codes": [{"code": a, "desc": b, "cls": c} for a, b, c in CODES],
            "nu": nu, "events": EVENTS,
            "eco": {"ic": {"CC": 120, "UPI": 90, "INTL": 150}, "sw": {"CC": .65, "UPI": .40, "INTL": 1.20}, "pf": {"CC": 2.0, "UPI": 0, "INTL": 0}}}


def main():
    ensure_demo()
    cards, offers, events, notyet = catalogs()
    data = {
        "meta": {"built_at": dt.datetime.now().strftime("%d %b %Y, %H:%M"), "focus_week": FOCUS_WEEK, "today": "2026-11-23", "buckets": BUCKETS},
        "tel": telemetry(), "findings": findings(), "cards": cards, "offers": offers, "events": events, "conflicts": conflicts(),
        "notyet": notyet, "syn": synthetic(cards), "portfolio": portfolio(),
        "demo_offer": {"merchant": "ZEPTO", "issuer": "IDFC FIRST Bank", "start": "2027-01-01", "end": "2027-01-07", "label": "IDFC offer at Zepto, ₹150 off ₹999+ (demo)"},
    }
    blob = json.dumps(data, ensure_ascii=False, default=str).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*PORTFOLIO*/", (ROOT / "scripts" / "portfolio_views.js").read_text(encoding="utf-8")).replace("/*DATA*/", blob).replace("/*ENGINE*/", ENGINE_JS.read_text(encoding="utf-8"))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB). Open it in your browser.")


if __name__ == "__main__":
    main()
