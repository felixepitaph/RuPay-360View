"""Read-only access to the CVP / MITC / offers / events catalogs and the merchant master.

The catalogs are the "cause" side of the platform: what was promised, charged or subsidised, and when.
Engines and agents use this module to ask "what changed around this date for this merchant or card?".
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _d(s):
    return dt.date.fromisoformat(s) if s else None


class Catalog:
    def __init__(self, dirs: list[str] | None = None):
        env = os.environ.get("R360_CATALOG_DIRS")
        self.dirs = [Path(p) for p in (dirs or (env.split(os.pathsep) if env else [ROOT / "catalog"]))]
        self.offers, self.cvp_cards, self.mitc, self.events, self.merchants = [], [], [], [], []
        self.categories = {}
        for d in self.dirs:
            for f in sorted(d.rglob("*.json")):
                data = json.loads(f.read_text())
                rel = f.as_posix()
                if f.name.startswith("offers_"):
                    for o in data:
                        o["_file"] = rel
                        self.offers.append(o)
                elif f.name.startswith("cvp_"):
                    for c in data["cards"]:
                        c["_issuer"] = data["issuer_bank"]
                        c["_file"] = rel
                        self.cvp_cards.append(c)
                elif f.name.startswith("mitc_"):
                    data["_file"] = rel
                    self.mitc.append(data)
                elif f.name.startswith("proposition_events"):
                    for e in data["events"]:
                        e["_file"] = rel
                        self.events.append(e)
                elif f.name == "merchant_master.json":
                    self.merchants.extend(data["merchants"])
                    self.categories.update(data.get("categories", {}))
        self._alias = {}
        for m in self.merchants:
            for a in [m["name"], m["merchant_id"], *m.get("aliases", [])]:
                self._alias[a.strip().lower()] = m

    # ---- merchants -------------------------------------------------------
    def merchant(self, name_or_id: str):
        return self._alias.get((name_or_id or "").strip().lower())

    def competitors(self, merchant_id: str):
        m = self.merchant(merchant_id)
        if not m:
            return []
        return [x for x in self.merchants if x["category"] == m["category"] and x["merchant_id"] != m["merchant_id"]]

    # ---- offers ----------------------------------------------------------
    def offer_merchant(self, o):
        return self.merchant(o.get("merchant_brand", ""))

    def offers_active(self, start: dt.date, end: dt.date, merchant_id=None, category=None, issuer=None):
        out = []
        for o in self.offers:
            v = o.get("validity", {})
            s, e = _d(v.get("start_date")) or dt.date.min, _d(v.get("end_date")) or dt.date.max
            if e < start or s > end:
                continue
            m = self.offer_merchant(o)
            if merchant_id and (not m or m["merchant_id"] != merchant_id):
                continue
            if category and (not m or m["category"] != category):
                continue
            if issuer and issuer.lower() not in (o.get("issuer_bank") or "").lower():
                continue
            overlap = (min(e, end) - max(s, start)).days + 1
            out.append({**o, "_merchant": m, "_overlap_days": overlap,
                        "_window_days": (end - start).days + 1})
        return out

    # ---- proposition events (CVP / MITC changes) --------------------------
    def events_between(self, start: dt.date, end: dt.date, issuer=None, card_ids=None):
        out = []
        for e in self.events:
            d = _d(e["effective_date"])
            if not (start <= d <= end):
                continue
            if issuer and issuer.lower() not in e["issuer_bank"].lower():
                continue
            if card_ids and e.get("card_ids") and not set(card_ids) & set(e["card_ids"]):
                continue
            out.append(e)
        return out

    # ---- cards -------------------------------------------------------------
    def card(self, card_id: str):
        return next((c for c in self.cvp_cards if c["card_id"] == card_id), None)

    # ---- free-text search for agents ------------------------------------------
    def search(self, text: str, limit: int = 20):
        words = [w for w in text.lower().split() if len(w) > 2]
        hits = []
        for kind, items in (("offer", self.offers), ("card", self.cvp_cards), ("event", self.events)):
            for it in items:
                blob = json.dumps(it, ensure_ascii=False).lower()
                score = sum(blob.count(w) for w in words)
                if score:
                    hits.append((score, kind, it))
        hits.sort(key=lambda x: -x[0])
        return [{"kind": k, "item": {kk: vv for kk, vv in it.items() if not kk.startswith("_m")}}
                for _, k, it in hits[:limit]]
