"""Command line = the tool interface. Every AiNxt tool and every scheduled job calls one of these
subcommands and reads JSON from stdout. Run `python -m r360 --help` (with PYTHONPATH=engine).

Examples
  python -m r360 run-insights --source local:demo/data --week 2027-01-04
  python -m r360 watch --source trino
  python -m r360 sql "SELECT merchant_id, SUM(spend) FROM agg_weekly_issuer_merchant GROUP BY 1"
  python -m r360 offers --start 2027-01-01 --end 2027-01-07 --category QUICK_COMMERCE
  python -m r360 catalog-search "forex markup YES"
  python -m r360 deal --scenario conservative
  python -m r360 verdict FND-abc123 CORRECT --note "Confirmed with issuer team"
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

from .catalog_store import Catalog
from .data_access import QueryBlocked, get_source
from .ledger import Ledger


def _out(obj):
    json.dump(obj, sys.stdout, indent=1, default=str, ensure_ascii=False)
    sys.stdout.write("\n")


def _weekly(src):
    return src.run_sql("SELECT week_start, issuer_bank, merchant_id, SUM(spend) AS spend, SUM(cards) AS cards "
                       "FROM agg_weekly_issuer_merchant GROUP BY week_start, issuer_bank, merchant_id",
                       purpose="watcher input")


def cmd_watch(a):
    from .watcher import scan
    _out(scan(_weekly(get_source(a.source)), weeks=[dt.date.fromisoformat(a.week)] if a.week else None))


def cmd_run_insights(a):
    from .investigate import investigate
    from .watcher import scan
    src, cat, led = get_source(a.source), Catalog(a.catalog.split(",") if a.catalog else None), Ledger(a.ledger)
    flags = scan(_weekly(src), weeks=[dt.date.fromisoformat(a.week)] if a.week else None)
    new = []
    for f in flags:
        b = investigate(f, src, cat)
        if led.add_finding(b):
            new.append(b)
    _out({"flags": len(flags), "new_findings": len(new),
          "headlines": [b["headline"] for b in new], "finding_ids": [b["finding_id"] for b in new]})


def cmd_sql(a):
    try:
        df = get_source(a.source).run_sql(a.query, purpose=a.purpose or "ad-hoc / agent")
    except QueryBlocked as e:
        _out({"blocked": str(e)})
        sys.exit(2)
    _out({"columns": list(df.columns), "rows": df.head(a.limit).to_dict("records"), "row_count": len(df)})


def cmd_offers(a):
    cat = Catalog(a.catalog.split(",") if a.catalog else None)
    res = cat.offers_active(dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end),
                            merchant_id=a.merchant, category=a.category, issuer=a.issuer)
    _out([{k: v for k, v in o.items() if k != "_merchant"} for o in res])


def cmd_catalog_search(a):
    _out(Catalog(a.catalog.split(",") if a.catalog else None).search(a.text, a.limit))


def cmd_deal(a):
    from .deal_engine import SCENARIOS, calc_all, default_variant
    variants = json.load(open(a.file)) if a.file else [default_variant("V1", 5)]
    cfg = json.load(open(a.config)) if a.config else None
    r = calc_all(variants, cfg, pm=SCENARIOS[a.scenario])
    r.pop("monthly")
    _out(r)


def cmd_verdict(a):
    _out(Ledger(a.ledger).add_verdict(a.finding_id, a.verdict, a.cause, a.note, a.by))


def cmd_scorecard(a):
    _out(Ledger(a.ledger).scorecard())


def cmd_findings(a):
    fs = Ledger(a.ledger).findings()
    _out(fs[-a.limit:] if a.full else [{k: f[k] for k in ("finding_id", "status", "headline")} for f in fs[-a.limit:]])


def cmd_briefing(a):
    from .briefing import render
    path = render(Ledger(a.ledger), a.out)
    _out({"written": str(path)})


def main(argv=None):
    p = argparse.ArgumentParser(prog="r360")
    p.add_argument("--source", default=None, help="trino | local:<folder> (default R360_SOURCE or local:demo/data)")
    p.add_argument("--catalog", default=None, help="comma-separated catalog folders (default R360_CATALOG_DIRS or catalog/)")
    p.add_argument("--ledger", default=None)
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("watch"); x.add_argument("--week"); x.set_defaults(f=cmd_watch)
    x = s.add_parser("run-insights"); x.add_argument("--week"); x.set_defaults(f=cmd_run_insights)
    x = s.add_parser("sql"); x.add_argument("query"); x.add_argument("--purpose"); x.add_argument("--limit", type=int, default=200); x.set_defaults(f=cmd_sql)
    x = s.add_parser("offers"); x.add_argument("--start", required=True); x.add_argument("--end", required=True)
    x.add_argument("--merchant"); x.add_argument("--category"); x.add_argument("--issuer"); x.set_defaults(f=cmd_offers)
    x = s.add_parser("catalog-search"); x.add_argument("text"); x.add_argument("--limit", type=int, default=10); x.set_defaults(f=cmd_catalog_search)
    x = s.add_parser("deal"); x.add_argument("--scenario", default="base", choices=["base", "conservative", "aggressive"])
    x.add_argument("--file"); x.add_argument("--config"); x.set_defaults(f=cmd_deal)
    x = s.add_parser("verdict"); x.add_argument("finding_id"); x.add_argument("verdict", choices=["CORRECT", "WRONG", "PARTLY"])
    x.add_argument("--cause"); x.add_argument("--note", default=""); x.add_argument("--by", default="analyst"); x.set_defaults(f=cmd_verdict)
    x = s.add_parser("scorecard"); x.set_defaults(f=cmd_scorecard)
    x = s.add_parser("findings"); x.add_argument("--limit", type=int, default=20); x.add_argument("--full", action="store_true"); x.set_defaults(f=cmd_findings)
    x = s.add_parser("briefing"); x.add_argument("--out", default="app/briefing.html"); x.set_defaults(f=cmd_briefing)
    a = p.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
