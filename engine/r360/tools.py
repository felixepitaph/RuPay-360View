"""The tool layer: every capability an AiNxt agent may use, as a named function with a JSON schema.

Rules built in:
  * Reads go through data_access (read-only, row cap, logged; column restrictions from engine/config/restrictions.json).
  * Agents never write to catalog/, ledger/ or engine/config directly. Write tools only create
    *proposals* in proposals/ which a human approves in the AiNxt Curator Queue (or a merge request).
  * Numbers returned here come from SQL or tested engines; agents must quote them, not recompute.

`SPECS` is exported in the function-calling format (name, description, input_schema) and served by
tools/server.py, so AiNxt Factory can register each one as a Tool.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from .catalog_store import Catalog
from .data_access import QueryBlocked, get_source
from .ledger import Ledger

ROOT = Path(__file__).resolve().parents[2]
PROPOSALS = ROOT / "proposals"
REGISTRY = ROOT / "catalog" / "sources" / "registry.json"


def _src(source=None):
    return get_source(source)


def r360_sql(query: str, purpose: str, source: str | None = None, limit: int = 500):
    try:
        df = _src(source).run_sql(query, purpose=purpose)
    except QueryBlocked as e:
        return {"blocked": str(e)}
    return {"columns": list(df.columns), "row_count": len(df), "rows": json.loads(df.head(limit).to_json(orient="records", date_format="iso"))}


def r360_describe_tables(source: str | None = None):
    """Lists tables the agent may query (semantic layer) with their columns."""
    src = _src(source)
    if src.name == "local":
        tabs = src.run_sql("SELECT table_name, column_name, data_type FROM information_schema.columns ORDER BY 1, ordinal_position", purpose="describe")
    else:
        tabs = src.run_sql("SELECT table_name, column_name, data_type FROM information_schema.columns "
                           "WHERE table_schema = current_schema ORDER BY 1, ordinal_position", purpose="describe")
    out = {}
    for r in tabs.itertuples():
        out.setdefault(r.table_name, []).append(f"{r.column_name} {r.data_type}")
    return out


def r360_run_insights(week: str | None = None, source: str | None = None, catalog: list[str] | None = None):
    from .investigate import investigate
    from .watcher import scan
    src, cat, led = _src(source), Catalog(catalog), Ledger()
    weekly = src.run_sql("SELECT week_start, issuer_bank, merchant_id, SUM(spend) AS spend, SUM(cards) AS cards "
                         "FROM agg_weekly_issuer_merchant GROUP BY week_start, issuer_bank, merchant_id", purpose="watcher input")
    flags = scan(weekly, weeks=[dt.date.fromisoformat(week)] if week else None)
    new = []
    for f in flags:
        b = investigate(f, src, cat)
        if led.add_finding(b):
            new.append(b)
    return {"flags": len(flags), "new_findings": [{"finding_id": b["finding_id"], "headline": b["headline"]} for b in new]}


def r360_get_finding(finding_id: str):
    return next((f for f in Ledger().findings() if f["finding_id"] == finding_id), {"error": "not found"})


def r360_list_findings(status: str | None = None, limit: int = 20):
    fs = [f for f in Ledger().findings() if not status or f["status"] == status]
    return [{"finding_id": f["finding_id"], "status": f["status"], "headline": f["headline"]} for f in fs[-limit:]]


def r360_offers_active(start: str, end: str, merchant: str | None = None, category: str | None = None, issuer: str | None = None):
    cat = Catalog()
    res = cat.offers_active(dt.date.fromisoformat(start), dt.date.fromisoformat(end), merchant_id=merchant, category=category, issuer=issuer)
    return [{k: v for k, v in o.items() if not k.startswith("_m")} for o in res]


def r360_catalog_search(text: str, limit: int = 10):
    return Catalog().search(text, limit)


def r360_card(card_id: str):
    return Catalog().card(card_id) or {"error": "not found"}


def r360_proposition_events(start: str, end: str, issuer: str | None = None):
    return Catalog().events_between(dt.date.fromisoformat(start), dt.date.fromisoformat(end), issuer=issuer)


def r360_deal_engine(variants: list | None = None, config: dict | None = None, scenario: str = "base"):
    from .deal_engine import SCENARIOS, calc_all, default_variant
    r = calc_all(variants or [default_variant("V1", 5)], config, pm=SCENARIOS[scenario])
    r.pop("monthly")
    return r


def r360_source_check(url: str, page_text: str):
    """Hash-diff for the Document agent: tells whether a page changed since the last approved read,
    so extraction (and its token cost) only runs on change."""
    reg = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else {"sources": {}}
    norm = " ".join(page_text.split())
    h = hashlib.sha256(norm.encode()).hexdigest()
    prev = reg["sources"].get(url, {}).get("content_hash")
    return {"url": url, "content_hash": h, "previous_hash": prev, "changed": h != prev}


def _propose(kind: str, payload: dict, reason: str, sources: list):
    if not sources:
        return {"error": "Every proposal needs at least one source (document or URL, locator, date)."}
    PROPOSALS.mkdir(exist_ok=True)
    pid = f"{kind}-{dt.datetime.now():%Y%m%d-%H%M%S}-{hashlib.sha1(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:6]}"
    rec = {"proposal_id": pid, "kind": kind, "status": "AWAITING_REVIEW", "reason": reason, "sources": sources,
           "payload": payload, "created_at": dt.datetime.now().isoformat(timespec="seconds")}
    (PROPOSALS / f"{pid}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False))
    return {"proposal_id": pid, "status": "AWAITING_REVIEW", "next": "Appears in the AiNxt Curator Queue for approval."}


def r360_propose_catalog_change(target_file: str, change: dict, reason: str, sources: list):
    return _propose("catalog", {"target_file": target_file, "change": change}, reason, sources)


def r360_propose_metric(name: str, definition: str, sql: str, why_useful: str, example_result: dict | None = None):
    try:
        _src().run_sql(sql, purpose=f"metric proposal check: {name}")
    except QueryBlocked as e:
        return {"error": f"SQL rejected: {e}"}
    return _propose("metric", {"name": name, "definition": definition, "sql": sql, "example_result": example_result},
                    why_useful, [{"document": "query_log", "locator": name, "retrieved_on": str(dt.date.today())}])


def r360_record_verdict(finding_id: str, verdict: str, true_cause: str | None = None, note: str = "", by: str = "analyst"):
    return Ledger().add_verdict(finding_id, verdict, true_cause, note, by)


def r360_scorecard():
    return Ledger().scorecard()


def r360_validate_catalog():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_catalog.py")], capture_output=True, text=True)
    return {"ok": r.returncode == 0, "output": r.stdout[-4000:]}


def _s(props, req):
    return {"type": "object", "properties": props, "required": req}


S, I, O, A = {"type": "string"}, {"type": "integer"}, {"type": "object"}, {"type": "array"}
SPECS = [
    ("r360_sql", r360_sql, "Run one READ-ONLY SQL query on the RuPay 360 semantic layer and get rows back. Use for any number you need, including new metrics you invent. Raw-table dumps over the row cap are refused, and any column restrictions in engine/config/restrictions.json apply. Always state the purpose.",
     _s({"query": S, "purpose": S, "limit": I}, ["query", "purpose"])),
    ("r360_describe_tables", r360_describe_tables, "List the tables and columns you may query.", _s({}, [])),
    ("r360_run_insights", r360_run_insights, "Run the Watcher on the latest (or given) week, investigate every flag against the catalogs and data, and save new findings to the ledger.",
     _s({"week": {"type": "string", "description": "Monday of the week, YYYY-MM-DD"}}, [])),
    ("r360_get_finding", r360_get_finding, "Get one finding's full evidence bundle (flag, candidate causes, tests with SQL, cautions).", _s({"finding_id": S}, ["finding_id"])),
    ("r360_list_findings", r360_list_findings, "List recent findings with headlines.", _s({"status": S, "limit": I}, [])),
    ("r360_offers_active", r360_offers_active, "Offers live in a date window, optionally for one merchant, category or issuer. Each offer carries its source.",
     _s({"start": S, "end": S, "merchant": S, "category": S, "issuer": S}, ["start", "end"])),
    ("r360_catalog_search", r360_catalog_search, "Keyword search across CVP cards, offers and proposition events.", _s({"text": S, "limit": I}, ["text"])),
    ("r360_card", r360_card, "Full CVP record for one card_id (e.g. YES_SELECT, IDFC_FIRST_WEALTH).", _s({"card_id": S}, ["card_id"])),
    ("r360_proposition_events", r360_proposition_events, "Dated CVP / MITC changes in a window, optionally for one issuer.", _s({"start": S, "end": S, "issuer": S}, ["start", "end"])),
    ("r360_deal_engine", r360_deal_engine, "Run the verified Deal Model V1.1 engine. Returns net / gross / incentive BPS, totals and per-year results. Never estimate deal economics yourself.",
     _s({"variants": A, "config": O, "scenario": {"type": "string", "enum": ["base", "conservative", "aggressive"]}}, [])),
    ("r360_source_check", r360_source_check, "Check whether a bank page or PDF text changed since the last approved extraction (hash compare). Extract only if changed.",
     _s({"url": S, "page_text": S}, ["url", "page_text"])),
    ("r360_propose_catalog_change", r360_propose_catalog_change, "Propose a change to a CVP, MITC, offers or events catalog file. Goes to the Curator Queue; never edits the catalog directly. Sources are mandatory.",
     _s({"target_file": S, "change": O, "reason": S, "sources": A}, ["target_file", "change", "reason", "sources"])),
    ("r360_propose_metric", r360_propose_metric, "Propose a new metric you found useful: name, plain definition, the SQL. The SQL is test-run first. Goes to the Curator Queue for the metric dictionary.",
     _s({"name": S, "definition": S, "sql": S, "why_useful": S, "example_result": O}, ["name", "definition", "sql", "why_useful"])),
    ("r360_record_verdict", r360_record_verdict, "Record an analyst's verdict on a finding (CORRECT, WRONG, PARTLY) with the true cause if known. Only when the analyst says so.",
     _s({"finding_id": S, "verdict": {"type": "string", "enum": ["CORRECT", "WRONG", "PARTLY"]}, "true_cause": S, "note": S, "by": S}, ["finding_id", "verdict"])),
    ("r360_scorecard", r360_scorecard, "Precision of past findings by cause type and confidence, from analyst verdicts.", _s({}, [])),
    ("r360_validate_catalog", r360_validate_catalog, "Validate all catalog files against their schemas.", _s({}, [])),
]
FUNCS = {n: f for n, f, _, _ in SPECS}


def spec_json():
    return [{"name": n, "description": d, "input_schema": sch} for n, _, d, sch in SPECS]
