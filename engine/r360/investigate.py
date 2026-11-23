"""Builds an evidence bundle for one Watcher flag: candidates from the catalogs, tests run on the data,
deterministic critic checks, and a confidence level. The bundle is what the AiNxt Investigator,
Critic and Writer agents read and add to; they cannot change its numbers.
"""
from __future__ import annotations

import datetime as dt

from . import evidence
from .causes import candidates
from .catalog_store import Catalog


def investigate(flag: dict, src, cat: Catalog, max_tested: int = 3) -> dict:
    cands = candidates(flag, cat)
    m = cat.merchant(flag["merchant_id"])
    tested = 0
    for c in cands:
        if c["type"] == "COMPETITOR_OFFER" and tested < max_tested:
            tests = [evidence.switching(src, flag, c["competitor_merchant_id"]),
                     evidence.eligibility_did(src, flag, c.get("issuer_of_offer")),
                     evidence.category_total(src, flag, m["category"])]
            c["tests"] = tests
            c["confidence"] = evidence.confidence(tests)
            tested += 1
        elif c["type"] in ("OWN_OFFER_STARTED", "OWN_OFFER_ENDED") and tested < max_tested:
            issuer = next((o.get("issuer_bank") for o in cat.offers if o["offer_id"] == c["offer_id"]), None)
            tests = [evidence.eligibility_did(src, flag, issuer),
                     evidence.category_total(src, flag, m["category"])]
            c["tests"] = tests
            c["confidence"] = evidence.confidence(tests)
            tested += 1
    best = next((c for c in cands if c.get("confidence") in ("HIGH", "MEDIUM")), None)
    checks = critic_checks(flag, cands, best)
    if best is None and cands and cands[0]["type"] in ("DATA_INCOMPLETE", "PORTFOLIO_WIDE"):
        best = cands[0]
    return {
        "finding_id": "FND-" + flag["flag_id"][2:],
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "status": "PROPOSED",
        "flag": flag,
        "merchant": {"merchant_id": flag["merchant_id"], "name": m["name"] if m else flag["merchant_id"],
                     "category": m["category"] if m else None},
        "candidates": cands,
        "best_explanation": _best(best),
        "critic_checks": checks,
        "headline": headline(flag, m, best),
        "narrative": None,          # written by the Writer agent from this bundle only
        "analyst_verdict": None,    # CORRECT / WRONG / PARTLY, set in the Curator Queue
    }


def critic_checks(flag, cands, best):
    out = []
    if flag.get("partial_week"):
        out.append("Data for this week looks incomplete; re-run after the next refresh before acting.")
    if flag.get("issuer_wide"):
        out.append("Most of this issuer's merchants moved the same way; look for a portfolio or data cause first.")
    if best and best.get("tests"):
        sw = next((t for t in best["tests"] if t["test"] == "SWITCHING"), None)
        if sw and sw["numbers"].get("cohort_cards", 0) < 100:
            out.append("Fewer than 100 cardholders in the switching cohort; treat as indicative.")
        if any(t["reading"] == "INCONCLUSIVE" for t in best["tests"]):
            out.append("At least one test was inconclusive.")
    top = [c for c in cands if c.get("confidence") in ("HIGH", "MEDIUM")]
    if len(top) > 1:
        out.append(f"{len(top)} candidate causes pass the tests; they may act together.")
    if not cands:
        out.append("No offer or proposition change in the catalogs explains this; check offers not yet catalogued "
                   "(network offers, other banks) and merchant-side events.")
    out.append("Association, not proof: the tests make the cause plausible; they do not rule out unseen events.")
    return out


def _best(c):
    if not c:
        return None
    return {k: c.get(k) for k in ("type", "summary", "offer_id", "event_id", "competitor_merchant_id",
                                   "confidence", "prior_score", "sources")}


def headline(flag, m, best):
    name = m["name"] if m else flag["merchant_id"]
    move = f"{name} spend on {flag['issuer_bank']} cards {'fell' if flag['direction'] == 'DROP' else 'rose'} " \
           f"{abs(flag['pct_change']):.0%} in the week of {flag['week_start']}"
    if not best:
        return move + "; cause not yet identified."
    if best["type"] == "COMPETITOR_OFFER":
        sw = next(t for t in best["tests"] if t["test"] == "SWITCHING")
        return (move + f"; likely drawn away by {best['summary'].split(' (')[0]} "
                f"({sw['numbers']['recapture_share']:.0%} of the lost spend reappeared there), "
                f"confidence {best['confidence'].lower()}.")
    if best["type"] in ("OWN_OFFER_STARTED", "OWN_OFFER_ENDED"):
        return move + f"; likely the {best['summary'].split(' (')[0]} " \
               f"{'starting' if best['type'] == 'OWN_OFFER_STARTED' else 'ending'}, confidence {best['confidence'].lower()}."
    return move + f"; possible cause: {best['summary']}."
