"""End-to-end check on the SYNTHETIC demo data: the planted causes must be found, and the
unexplained drop must stay unexplained (no invented cause)."""
import subprocess
import sys
from pathlib import Path

import pytest

from r360.catalog_store import Catalog
from r360.data_access import LocalSource, QueryBlocked
from r360.investigate import investigate
from r360.watcher import scan
import datetime as dt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "demo" / "data"


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    if not (DATA / "txn_weekly_card_merchant.parquet").exists():
        subprocess.run([sys.executable, str(ROOT / "demo" / "make_synthetic.py")], check=True)
    src = LocalSource(str(DATA), log_path=str(tmp_path_factory.mktemp("q") / "log.jsonl"))
    cat = Catalog([str(ROOT / "catalog"), str(ROOT / "demo" / "catalog")])
    wk = src.run_sql("SELECT week_start, issuer_bank, merchant_id, SUM(spend) AS spend, SUM(cards) AS cards "
                     "FROM agg_weekly_issuer_merchant GROUP BY 1, 2, 3")
    flags = scan(wk, weeks=[dt.date(2027, 1, 4)])
    return src, {(f["issuer_bank"], f["merchant_id"]): investigate(f, src, cat) for f in flags}


def test_three_planted_moves_flagged(run):
    _, found = run
    assert set(found) == {("IDFC FIRST Bank", "BLINKIT"), ("IDFC FIRST Bank", "ZEPTO"), ("YES BANK", "SWIGGY")}


def test_blinkit_drop_explained_by_competitor_offer(run):
    b = run[1][("IDFC FIRST Bank", "BLINKIT")]["best_explanation"]
    assert b["type"] == "COMPETITOR_OFFER" and b["competitor_merchant_id"] == "ZEPTO" and b["confidence"] == "HIGH"


def test_zepto_rise_explained_by_own_offer(run):
    b = run[1][("IDFC FIRST Bank", "ZEPTO")]["best_explanation"]
    assert b["type"] == "OWN_OFFER_STARTED"


def test_swiggy_drop_left_unexplained(run):
    assert run[1][("YES BANK", "SWIGGY")]["best_explanation"] is None


def test_guards(run):
    src = run[0]
    with pytest.raises(QueryBlocked):
        src.run_sql("DELETE FROM agg_weekly_issuer_merchant")
    with pytest.raises(QueryBlocked):
        src.run_sql("SELECT 1 AS pan")
    with pytest.raises(QueryBlocked):
        src.run_sql("SELECT * FROM txn_weekly_card_merchant")  # over the row cap
