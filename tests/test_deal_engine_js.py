"""The browser copy of the Deal Model (engine/js/deal_engine.js) must match the Python engine."""
import json, shutil, subprocess, itertools
from pathlib import Path
import pytest
from r360.deal_engine import SCENARIOS, DEFAULT_CONFIG, calc_all, default_variant

ROOT = Path(__file__).resolve().parent.parent
NODE = shutil.which("node")

PMS = list(SCENARIOS.values()) + [dict(SCENARIOS["base"], cif=a, volume=b, activation=c, ats=d)
                                  for a, b, c, d in itertools.product([.7, 1.3], [.8, 1.2], [.9], [.6, 1.4])]


@pytest.mark.skipif(NODE is None, reason="node not installed")
def test_js_matches_python():
    js = ("const E=require(%r);const pms=%s;console.log(JSON.stringify(pms.map(pm=>{const r=E.calcAll([E.defaultVariant('V1',5)],E.DEFAULT_CONFIG,null,null,pm);"
          "return [r.net_bps,r.gross_bps,r.total_spends,r.net_revenue]})))") % (str(ROOT / "engine/js/deal_engine.js"), json.dumps(PMS))
    got = json.loads(subprocess.run([NODE, "-e", js], capture_output=True, text=True, check=True).stdout)
    for pm, g in zip(PMS, got):
        r = calc_all([default_variant("V1", 5)], DEFAULT_CONFIG, pm=pm)
        for a, b in zip(g, [r["net_bps"], r["gross_bps"], r["total_spends"], r["net_revenue"]]):
            assert abs(a - b) <= 1e-9 * max(1, abs(b)), (pm, a, b)
