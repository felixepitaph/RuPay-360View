"""Reference numbers from docs/reference/01_master_blueprint.md (Deal Model V1.1 default state)."""
from r360.deal_engine import default_variant, calc_all, SCENARIOS, DEFAULT_CONFIG

def model(pm=None):
    return calc_all([default_variant("V1", 5)], DEFAULT_CONFIG, pm=pm)

def test_closing_cif():
    ys = model()["years"]
    assert [round(y["cif"]) for y in ys] == [60000, 120000, 180000, 240000, 300000]

def test_derived_attrition():
    rates = model()["variants"][0]["derived_attrition"]
    assert [round(r * 100, 3) for r in rates] == [0.0, 3.805, 4.607, 4.961, 5.161]

def test_totals_and_bps():
    m = model()
    assert round(m["total_spends"] / 1e7, 1) == 16596.0
    assert round(m["total_revenue"] / 1e7, 3) == 65.672
    assert round(m["total_incentives"] / 1e7, 3) == 39.125
    assert round(m["net_revenue"] / 1e7, 3) == 26.547
    assert round(m["gross_bps"], 2) == 39.57
    assert round(m["incentive_bps"], 2) == 23.57
    assert round(m["net_bps"], 3) == 15.996

def test_scenarios():
    got = {k: round(model(pm)["net_bps"], 2) for k, pm in SCENARIOS.items()}
    assert got == {"base": 16.0, "conservative": 24.05, "aggressive": 13.47}
