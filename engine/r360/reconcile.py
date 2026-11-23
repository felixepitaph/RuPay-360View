"""Reconcile web CVP entries against the issuer MITC: fees, forex markup, fuel-waiver cap.
Rule: fees follow the MITC; differences are listed for the analyst (Reconciler harness uses this)."""
from __future__ import annotations

import re

from .catalog_store import Catalog

CARD_TO_MITC = {
    "YES_MARQUEE": "Marquee", "YES_ELITE_PLUS": "Elite+", "YES_ESSENCE": "YES Essence", "YES_SELECT": "Select",
    "YES_ACE": "Ace", "YES_PROSPERITY_REWARDS": "YES Prosperity Rewards", "YES_PROSPERITY_CASHBACK_PLUS": "YES Prosperity Cashback Plus",
    "YES_PROSPERITY_CASHBACK": "YES Prosperity Cashback", "YES_UNI": "Uni", "YES_AI_INSIDE": "Klick / Zagg / Finbooster / AI Inside / NIYO / Novio / Max",
    "YES_NIYO": "Klick / Zagg / Finbooster / AI Inside / NIYO / Novio / Max",
    "IDFC_FIRST_WEALTH": "FIRST Wealth", "IDFC_FIRST_SELECT": "FIRST Select", "IDFC_FIRST_MILLENNIA": "FIRST Millennia",
    "IDFC_FIRST_CLASSIC": "FIRST Classic", "IDFC_FIRST_WOW": "FIRST WOW!", "IDFC_FIRST_WOW_BLACK": "FIRST WOW! Black",
    "IDFC_QUANTUM_PLUS": "Quantum+", "IDFC_HELLO_CASHBACK": "Hello Cashback", "IDFC_FIRST_POWER_PLUS": "FIRST Power+",
    "IDFC_FIRST_POWER": "FIRST Power", "IDFC_MAYURA": "Mayura",
}


RULE_NAME = {"YES_AI_INSIDE": "AI Inside", "YES_NIYO": "NIYO"}  # name used in the MITC's rule tables


def _num(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    m = re.search(r"[\d.]+", str(x).replace(",", ""))
    return float(m.group()) if m else None


def _rule(rows, variant, short):
    for r in rows:
        vs = r.get("variants", [])
        if short in vs or variant in vs or "All variants" in vs:
            return r
    return None


def reconcile(cat: Catalog | None = None):
    cat = cat or Catalog()
    mitc = {m["issuer_bank"]: m for m in cat.mitc}
    out = []
    for c in cat.cvp_cards:
        v = CARD_TO_MITC.get(c["card_id"])
        m = next((mm for k, mm in mitc.items() if k.split()[0].lower() in c["_issuer"].lower()), None)
        if not v or not m:
            out.append({"card_id": c["card_id"], "field": "mapping", "status": "NO_MITC_MATCH"})
            continue
        row = next((r for r in m["variants"] if r["variant"] == v), None)
        short = RULE_NAME.get(c["card_id"], v.split(" / ")[0])
        fees = c.get("fees", {})
        checks = [("joining_fee_inr", _num(fees.get("joining_inr")), _num(row and row.get("joining_fee_inr"))),
                  ("annual_fee_inr", _num(fees.get("annual_inr")), _num(row and row.get("annual_fee_inr")))]
        fx = _rule(m.get("forex", []), v, short)
        page_fx = _num((c.get("forex") or {}).get("markup_text")) if any(ch.isdigit() for ch in str((c.get("forex") or {}).get("markup_text"))) else 0.0
        checks.append(("forex_markup_pct", page_fx, _num(fx and fx.get("forex_markup_pct"))))
        fu = _rule(m.get("fuel_surcharge_waiver", []), v, short)
        page_cap = re.search(r"(?:capped|up to|max(?:imum)?[^R]*)\s*Rs\s?([\d,]+)", str(c.get("fuel_surcharge_waiver")), re.I)
        checks.append(("fuel_waiver_cap_inr", _num(page_cap.group(1)) if page_cap else None,
                       _num(fu and (fu.get("max_waiver_per_cycle_inr") or fu.get("max_waiver_per_statement_cycle_inr")))))
        for field, page, doc in checks:
            if page is None or doc is None:
                status = "MISSING_ON_PAGE" if page is None and doc is not None else ("MISSING_IN_MITC" if doc is None and page is not None else "NOT_STATED_EITHER")
            else:
                status = "MATCH" if abs(page - doc) < 1e-6 else "CONFLICT"
            out.append({"card_id": c["card_id"], "mitc_variant": v, "field": field, "page_value": page, "mitc_value": doc,
                        "status": status, "rule": "MITC wins" if status == "CONFLICT" and field != "fuel_waiver_cap_inr" else None})
    return out
