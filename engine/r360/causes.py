"""Candidate causes for a Watcher flag, looked up in the catalogs by date, merchant and issuer.

This is a *prior*: it lists what could explain the move and scores how well each fits on timing,
category and issuer. The Evidence tests then check each candidate against the data. Scores are
heuristic and transparent (every component is returned) so the Critic and the analyst can see why.
"""
from __future__ import annotations

import datetime as dt

from .catalog_store import Catalog

CATEGORY_TO_EVENT_TAGS = {  # merchant category -> event affected_categories that touch it
    "TRAVEL_BUS": {"TRAVEL", "RAILWAYS"}, "TRAVEL_OTA": {"TRAVEL", "INTERNATIONAL"},
    "DINING_ENTERTAINMENT": {"DINING", "MOVIES"}, "BILL_PAYMENTS": {"UTILITIES", "INSURANCE", "EDUCATION"},
}


def _benefit_size(o):
    b = o.get("benefit", {})
    if b.get("rate_pct"):
        return min(b["rate_pct"] / 20.0, 1.0)  # 20% or more counts as maximal
    if b.get("flat_inr"):
        return min(b["flat_inr"] / 250.0, 1.0)  # Rs250 flat or more counts as maximal
    return 0.3


def candidates(flag: dict, cat: Catalog, lookback_days: int = 14) -> list[dict]:
    wk = dt.date.fromisoformat(flag["week_start"])
    w_start, w_end = wk, wk + dt.timedelta(days=6)
    m = cat.merchant(flag["merchant_id"])
    category = m["category"] if m else None
    issuer = flag["issuer_bank"]
    drop = flag["direction"] == "DROP"
    out = []

    # 1. Offers at competing merchants in the same category, live during the week
    if category:
        for o in cat.offers_active(w_start, w_end, category=category):
            om = o["_merchant"]
            if om["merchant_id"] == flag["merchant_id"]:
                continue
            same_iss = issuer.lower() in (o.get("issuer_bank") or "").lower()
            comp = {"timing": round(o["_overlap_days"] / o["_window_days"], 2),
                    "same_category": 1.0, "same_issuer": 1.0 if same_iss else 0.5,
                    "benefit_size": round(_benefit_size(o), 2), "direction_fit": 1.0 if drop else 0.2}
            out.append({"type": "COMPETITOR_OFFER", "summary":
                        f"{o.get('issuer_bank') or o.get('offer_source')} offer at {om['name']} "
                        f"({_benefit_text(o)}) live {o['validity'].get('start_date')} to {o['validity'].get('end_date')}",
                        "competitor_merchant_id": om["merchant_id"], "offer_id": o["offer_id"],
                        "issuer_of_offer": o.get("issuer_bank"), "sources": o.get("sources", []),
                        "components": comp})

    # 2. Offers at the same merchant that started (explains a rise) or ended (explains a drop)
    if m:
        near = cat.offers_active(w_start - dt.timedelta(days=lookback_days), w_end, merchant_id=m["merchant_id"])
        for o in near:
            v = o["validity"]
            end = dt.date.fromisoformat(v["end_date"]) if v.get("end_date") else None
            start = dt.date.fromisoformat(v["start_date"]) if v.get("start_date") else None
            ended = end and w_start - dt.timedelta(days=lookback_days) <= end < w_start
            started = start and w_start - dt.timedelta(days=3) <= start <= w_end
            if (drop and ended) or (not drop and started):
                out.append({"type": "OWN_OFFER_ENDED" if drop else "OWN_OFFER_STARTED",
                            "summary": f"{o.get('issuer_bank')} offer at {m['name']} ({_benefit_text(o)}) "
                                       f"{'ended ' + v['end_date'] if drop else 'started ' + v['start_date']}",
                            "offer_id": o["offer_id"], "sources": o.get("sources", []),
                            "components": {"timing": 1.0, "same_category": 1.0,
                                           "same_issuer": 1.0 if issuer.lower() in (o.get('issuer_bank') or '').lower() else 0.5,
                                           "benefit_size": round(_benefit_size(o), 2), "direction_fit": 1.0}})

    # 3. CVP / MITC changes taking effect shortly before or during the week
    tags = CATEGORY_TO_EVENT_TAGS.get(category, set()) | ({category} if category else set()) | {"ALL"}
    for e in cat.events_between(w_start - dt.timedelta(days=lookback_days), w_end, issuer=issuer):
        hit = tags & set(e.get("affected_categories", []))
        if not hit:
            continue
        fits = (e["direction"] == "DEVALUATION") == drop
        out.append({"type": "PROPOSITION_CHANGE", "summary": f"{e['event_type']} {e['effective_date']}: {e['description']}",
                    "event_id": e["event_id"], "sources": e.get("sources", []),
                    "components": {"timing": 1.0, "same_category": 1.0 if category in hit else 0.6,
                                   "same_issuer": 1.0, "benefit_size": 0.5, "direction_fit": 1.0 if fits else 0.2}})

    # 4. Context: data problem or portfolio-wide move
    if flag.get("partial_week"):
        out.append({"type": "DATA_INCOMPLETE", "summary": f"Issuer volume that week is {flag.get('volume_ratio_vs_normal')}x normal; data may be late",
                    "components": {"timing": 1.0, "same_category": 1.0, "same_issuer": 1.0, "benefit_size": 1.0, "direction_fit": 1.0}})
    if flag.get("issuer_wide"):
        out.append({"type": "PORTFOLIO_WIDE", "summary": f"{int(flag.get('issuer_wide_share', 0) * 100)}% of this issuer's merchants moved the same way",
                    "components": {"timing": 1.0, "same_category": 0.5, "same_issuer": 1.0, "benefit_size": 0.8, "direction_fit": 1.0}})

    for c in out:
        comp = c["components"]
        c["prior_score"] = round(comp["timing"] * comp["same_category"] * comp["same_issuer"]
                                 * (0.5 + 0.5 * comp["benefit_size"]) * comp["direction_fit"], 3)
    return sorted(out, key=lambda c: -c["prior_score"])


def _benefit_text(o):
    b = o.get("benefit", {})
    if b.get("rate_pct"):
        t = f"{b['rate_pct']}% off"
    elif b.get("flat_inr"):
        t = f"Rs{b['flat_inr']:,} off"
    else:
        t = b.get("type", "offer").lower()
    if b.get("min_txn_inr"):
        t += f" on Rs{b['min_txn_inr']:,}+"
    return t + (f", {o['payment_mode']}" if o.get("payment_mode") not in (None, "ANY") else "")
