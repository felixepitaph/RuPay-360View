"""Build app/platform_preview.html: a single-file, clickable preview of all five RuPay 360 modules.

REAL: card/offer/event catalogs, catalog conflicts, Deal Model engine results, findings (engine output on demo data).
SYNTHETIC: all spend, card counts, network split and wallet share (demo/data + seeded RNG here).

Run from the repo root:
    PowerShell:  $env:PYTHONPATH="engine"; python scripts/build_preview.py
    bash:        PYTHONPATH=engine python scripts/build_preview.py
Then open app/platform_preview.html in a browser.
"""
from __future__ import annotations

import datetime as dt
import itertools
import json
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))

from r360.deal_engine import SCENARIOS, DEFAULT_CONFIG, calc_all, default_variant  # noqa: E402

OUT = ROOT / "app" / "platform_preview.html"
TEMPLATE = ROOT / "scripts" / "preview_template.html"
DEMO = ROOT / "demo" / "data"
LEDGER = ROOT / "runs" / "demo_ledger" / "findings.jsonl"
FOCUS_WEEK = "2027-01-04"
ISSUERS = ["YES BANK", "IDFC FIRST Bank"]
CONTROL = "OTHER ISSUERS (control)"


def jload(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


# ---------- findings + weekly series (synthetic demo data, engine-made findings) ----------
def ensure_demo():
    if not DEMO.exists() or not (DEMO / "agg_weekly_issuer_merchant.parquet").exists():
        subprocess.run([sys.executable, str(ROOT / "demo" / "make_synthetic.py")], check=True, cwd=ROOT)
    if not LEDGER.exists():
        import os
        env = {**os.environ, "PYTHONPATH": str(ROOT / "engine"), "R360_SOURCE": "local:demo/data",
               "R360_QUERY_LOG": "runs/query_log.jsonl"}
        subprocess.run([sys.executable, "-m", "r360", "--ledger", "runs/demo_ledger", "run-insights",
                        "--week", FOCUS_WEEK], check=True, cwd=ROOT, env=env)


def weekly():
    import duckdb
    con = duckdb.connect()
    rows = con.execute(
        f"select cast(week_start as varchar), issuer_bank, sum(spend), sum(cards) "
        f"from '{(DEMO / 'agg_weekly_issuer_merchant.parquet').as_posix()}' group by 1,2 order by 1").fetchall()
    weeks = sorted({r[0] for r in rows})
    spend = {k: [0.0] * len(weeks) for k in ISSUERS + [CONTROL]}
    cards = {k: [0] * len(weeks) for k in ISSUERS + [CONTROL]}
    for w, i, s, c in rows:
        if i in spend:
            spend[i][weeks.index(w)] = s
            cards[i][weeks.index(w)] = int(c)
    return {"weeks": weeks, "spend": spend, "cards": cards}


def findings():
    out = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        f = json.loads(line)
        best = f.get("best_explanation")
        conf = best["confidence"] if best else None
        out.append({"id": f["finding_id"], "status": f["status"], "issuer": f["flag"]["issuer_bank"],
                    "merchant": f["merchant"]["name"], "week": f["flag"]["week_start"], "z": f["flag"]["robust_z"],
                    "pct": f["flag"]["pct_change"], "headline": f["headline"], "confidence": conf, "best": best,
                    "candidates": [{"summary": c["summary"], "prior_score": c["prior_score"],
                                    "tests": [{k: t[k] for k in ("test", "reading", "plain_english", "sql")}
                                              for t in c["tests"]]} for c in f["candidates"]]})
    out.sort(key=lambda f: -abs(f["pct"]))
    return out


# ---------- catalogs (real) ----------
def catalogs():
    cards = []
    notyet = {}
    for issuer, path in (("YES BANK", "catalog/yes_bank/cvp_yes_2026-11-23.json"),
                         ("IDFC FIRST Bank", "catalog/idfc_first/cvp_idfc_2026-11-23.json")):
        d = jload(path)
        notyet[issuer] = d.get("not_yet_extracted", [])
        for c in d["cards"]:
            fees = c.get("fees") or {}
            lg = c.get("lounge") or {}
            fx = c.get("forex") or {}
            earn = []
            if isinstance(c.get("earn_rules"), list):
                for e in c["earn_rules"]:
                    earn.append({"cat": e.get("category"), "rate": e.get("rate_text"), "cap": e.get("cap_text")})
            src = c.get("source") or {}
            cards.append({
                "id": c["card_id"], "name": c["card_name"], "issuer": issuer, "network": c.get("network"),
                "backing": c.get("backing"), "joining": fees.get("joining_inr"), "annual": fees.get("annual_inr"),
                "waiver": fees.get("annual_waiver_spend_inr"), "forex": fx.get("markup_text"),
                "lounge_dom": lg.get("domestic"), "lounge_int": lg.get("international"),
                "fuel": c.get("fuel_surcharge_waiver"),
                "reward_name": (c.get("reward_currency") or {}).get("name") if isinstance(c.get("reward_currency"), dict) else None,
                "eligibility": json.dumps(c["eligibility"]) if c.get("eligibility") else None,
                "welcome": c.get("welcome_benefits") if isinstance(c.get("welcome_benefits"), list) else [],
                "verified": c.get("verification_status"), "earn": earn,
                "conflicts": c.get("page_conflicts") or [], "source": src.get("url", "")})
    offers = []
    for issuer, path in (("IDFC FIRST Bank", "catalog/idfc_first/offers_idfc_nov2026_booklet.json"),
                         ("YES BANK", "catalog/yes_bank/offers_yes_credit_live_2026-11-23.json")):
        for o in jload(path):
            b = o.get("benefit") or {}
            parts = []
            if b.get("rate_pct") is not None:
                parts.append(f"{b['rate_pct']}% off")
            if b.get("flat_inr") is not None:
                parts.append(f"₹{b['flat_inr']:g} off")
            if b.get("min_txn_inr"):
                parts.append(f"on ₹{b['min_txn_inr']:g}+")
            if b.get("max_inr"):
                parts.append(f"up to ₹{b['max_inr']:g}")
            ben = " ".join(parts) or (b.get("type") or "").replace("_", " ").lower()
            v = o.get("validity") or {}
            s = (o.get("sources") or [{}])[0]
            offers.append({"issuer": issuer, "merchant": o.get("merchant_brand") or "", "category": o.get("category") or "",
                           "mode": o.get("payment_mode"), "benefit": ben, "cond": (o.get("conditions") or "")[:160],
                           "start": v.get("start_date"), "end": v.get("end_date"),
                           "dow": ",".join(v.get("days_of_week") or []),
                           "source": (s.get("document") or "").split("/")[-1][:48] + (" · " + s["locator"] if s.get("locator") else ""),
                           "ncards": len(o.get("eligible_cards") or [])})
    ev = jload("catalog/events/proposition_events.json")
    ev = ev.get("events", ev) if isinstance(ev, dict) else ev
    events = [{"date": e["effective_date"], "issuer": e["issuer_bank"], "type": e["event_type"],
               "direction": e.get("direction"), "desc": e["description"], "cards": e.get("card_ids") or []}
              for e in sorted(ev, key=lambda e: e["effective_date"], reverse=True)]
    return cards, offers, events, notyet


def conflicts():
    text = (ROOT / "docs" / "RECONCILIATION_2026-11-23.md").read_text(encoding="utf-8")
    sec = text.split("## Conflicts", 1)[1].split("\n## ", 1)[0]
    rows = []
    for ln in sec.splitlines():
        if ln.startswith("|") and not ln.startswith("|---") and not ln.startswith("| Card"):
            rows.append([c.strip() for c in ln.strip().strip("|").split("|")])
    return rows


# ---------- Deal Model (real engine) ----------
def deal():
    base = default_variant("V1", 5)

    def run(pm):
        r = calc_all([base], DEFAULT_CONFIG, pm=pm)
        return {"net_bps": r["net_bps"], "gross_bps": r["gross_bps"], "incentive_bps": r["incentive_bps"],
                "net_rev": r["net_revenue"], "spends": r["total_spends"],
                "years": [{k: y[k] for k in ("year", "cif", "spends", "revenue", "incentives", "net")} for y in r["years"]]}

    levels = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
    runs = {}
    for a, b, c in itertools.product(range(7), repeat=3):
        pm = {**SCENARIOS["base"], "cif": levels[a], "volume": levels[b], "activation": levels[c]}
        runs[f"{a}-{b}-{c}"] = run(pm)
    return {"presets": {k: run(v) for k, v in SCENARIOS.items()}, "grid": {"levels": levels, "runs": runs},
            "corridor": {"floor": DEFAULT_CONFIG["bpF"], "ceiling": DEFAULT_CONFIG["bpC"]}}


# ---------- Wallet share (SYNTHETIC, seeded) ----------
def wallet(weeks):
    rng = random.Random(360)
    cats = ["Dining", "Groceries & quick commerce", "Fuel", "Travel", "Shopping", "Utilities & bills", "Entertainment"]
    out = {}
    for k, base in (("YES BANK", 0.16), ("IDFC FIRST Bank", 0.27)):
        cl = []
        for c in cats:
            r = max(0.04, base + rng.uniform(-0.08, 0.1))
            v = rng.uniform(0.3, 0.5) * (1 - r)
            cl.append({"name": c, "rupay": round(r, 3), "visa": round(v, 3), "mc": round(1 - r - v, 3)})
        tr, x = [], base
        for _ in weeks:
            x = min(0.6, max(0.02, x + rng.uniform(-0.006, 0.01)))
            tr.append(round(x, 4))
        raw = [rng.uniform(0.5, 1.5) for _ in range(5)]
        s = sum(raw)
        out[k] = {"categories": cl, "rupay_trend": tr, "wallet_bands": [round(v / s, 3) for v in raw]}
    return out


def coverage(cards, offers, notyet):
    return {"cards": len(cards), "by_issuer": {k: sum(c["issuer"] == k for c in cards) for k in ISSUERS},
            "offers": len(offers), "offers_by": {k: sum(o["issuer"] == k for o in offers) for k in ISSUERS},
            "no_network": sum(not c["network"] for c in cards), "no_cards": sum(o["ncards"] == 0 for o in offers),
            "not_yet": notyet}


def main():
    ensure_demo()
    wk = weekly()
    cards, offers, events, notyet = catalogs()
    data = {
        "meta": {"built_at": dt.date.today().isoformat(), "focus_week": FOCUS_WEEK, "offer_date_default": "2026-11-23"},
        "weekly": wk, "findings": findings(),
        "markers": [{"from": "2027-01-04", "to": "2027-01-04", "label": "Zepto offer (1-7 Jan)"}],
        "cards": cards, "offers": offers, "events": events, "conflicts": conflicts(),
        "coverage": coverage(cards, offers, notyet), "wallet": wallet(wk["weeks"]), "deal": deal(),
    }
    blob = json.dumps(data, ensure_ascii=False, default=str).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*DATA*/", blob)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB). Open it in your browser.")


if __name__ == "__main__":
    main()
