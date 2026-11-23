#!/usr/bin/env bash
# End-to-end demo on SYNTHETIC data: watcher -> causes -> evidence -> ledger -> briefing page.
set -e
cd "$(dirname "$0")/.."
export PYTHONPATH=engine R360_SOURCE=local:demo/data R360_QUERY_LOG=runs/query_log.jsonl
python demo/make_synthetic.py
python -m r360 --catalog catalog,demo/catalog --ledger runs/demo_ledger run-insights --week 2027-01-04
python -m r360 --ledger runs/demo_ledger briefing --out app/briefing_demo.html
echo "Open app/briefing_demo.html in a browser."
