"""Deal Model V1.1 calculation engine, ported line for line from App.jsx (calcV, calcAll,
deriveMonthlyAttrition). No UI. Verified by tests/test_deal_engine.py against the blueprint
reference numbers. Do not change the maths without updating the tests and docs/DECISIONS.md.

Units: rupees, counts, rates as fractions. Fiscal months Apr..Mar.
"""
from __future__ import annotations

import copy

PARAMS = ["issuances", "activationCC", "txCC", "atsCC", "activationUPI", "txUPI", "atsUPI", "intlPct"]
EVEN = [1 / 12] * 12
SEASONALITY_PRESETS = {
    "flat": EVEN,
    "festive": [.06, .06, .07, .07, .07, .07, .09, .10, .13, .10, .09, .09],
    "q4": [.065, .065, .07, .07, .075, .08, .085, .09, .095, .10, .105, .10],
    "ramp": [.055, .06, .065, .07, .075, .08, .085, .09, .095, .10, .11, .115],
}

# rvp revenue per rupee spent, rff revenue per txn, ifp intl fee pct, iip intl incentive pct,
# imip intl milestone pct, mcb milestone card-fee bonus, msb milestone spend bonus, upf upfront,
# bpF / bpC net-BPS floor and ceiling (corridor display only)
DEFAULT_CONFIG = {"rvp": .0008, "rff": 2.4, "ifp": .015, "intlRevShare": .25, "iip": .002,
                  "imip": .001, "mcb": .10, "msb": .0001, "upf": 5e6, "bpF": 6, "bpC": 14,
                  "milestone_rule": "cif"}
# volume slabs on monthly portfolio txns: fb per txn, pb per rupee; CIF slabs on card-fee share
DEFAULT_VOLUME_SLABS = [{"t": 0, "fb": 1.2, "pb": .0002}, {"t": 1e6, "fb": 1.4, "pb": .00025},
                        {"t": 2e6, "fb": 1.6, "pb": .0003}, {"t": 4e6, "fb": 1.8, "pb": .00035}]
DEFAULT_CIF_SLABS = [{"t": 0, "pb": .5}, {"t": 1e6, "pb": .6}, {"t": 2e6, "pb": .65}, {"t": 3e6, "pb": .7}]

SCENARIOS = {
    "base": {"cif": 1, "volume": 1, "activation": 1, "ats": 1, "intl": 1},
    "conservative": {"cif": .85, "volume": .85, "activation": .9, "ats": .95, "intl": .9},
    "aggressive": {"cif": 1.15, "volume": 1.15, "activation": 1.1, "ats": 1.05, "intl": 1.1},
}


def default_variant(name: str = "V1", years: int = 5) -> dict:
    r = range(years)
    return {
        "name": name, "years": years, "cardFee": 100,
        "cif": [(i + 1) * 60000 for i in r],
        "issuances": [(i + 1) * 45000 + 15000 for i in r],
        "activationCC": [.3 + i * .05 for i in r], "txCC": [4 + i for i in r],
        "atsCC": [3000 + i * 400 for i in r],
        "activationUPI": [.15 + i * .06 for i in r], "txUPI": [6 + i * 2 for i in r],
        "atsUPI": [800 + i * 150 for i in r], "intlPct": [.05 + i * .01 for i in r],
        "seasonality": {k: list(EVEN) for k in PARAMS},
    }


def _slab(v, slabs):
    r = slabs[0]
    for s in slabs:
        if v >= s["t"]:
            r = s
        else:
            break
    return r


def derive_monthly_attrition(start_cif, target_end_cif, monthly_iss):
    lo, hi, best = 0.0, 0.15, 0.008
    for _ in range(50):
        mid = (lo + hi) / 2
        cif = start_cif
        for m in monthly_iss:
            cif = max(0.0, cif + m - mid * (cif + m))
        if cif > target_end_cif:
            lo = mid
        else:
            hi = mid
        best = mid
    return max(0.0, min(0.15, best))


def derived_attrition_rates(v):
    sn = v["seasonality"]["issuances"]
    t = sum(sn) or 1
    rates, prev = [], 0.0
    for y in range(v["years"]):
        iss = [v["issuances"][y] * (sn[m] / t) for m in range(12)]
        rate = derive_monthly_attrition(prev, v["cif"][y], iss)
        rates.append(rate)
        cif = prev
        for m in range(12):
            cif = max(0.0, cif + iss[m] - rate * (cif + iss[m]))
        prev = cif
    return rates


def _dist(ann, sn, kind):
    t = sum(sn) or 1
    out = []
    for a in ann:
        for i in range(12):
            out.append(a * sn[i] / t if kind == "sum" else a * sn[i] / (t / 12))
    return out


def calc_variant(v, pm):
    n = v["years"] * 12
    s = v["seasonality"]
    iss = [x * pm.get("cif", 1) for x in _dist(v["issuances"], s["issuances"], "sum")]
    rates = derived_attrition_rates(v)
    mA = [rates[m // 12] for m in range(n)]
    acC = [min(x * pm.get("activation", 1), 1) for x in _dist(v["activationCC"], s["activationCC"], "avg")]
    acU = [min(x * pm.get("activation", 1), 1) for x in _dist(v["activationUPI"], s["activationUPI"], "avg")]
    tC = [x * pm.get("volume", 1) for x in _dist(v["txCC"], s["txCC"], "avg")]
    tU = [x * pm.get("volume", 1) for x in _dist(v["txUPI"], s["txUPI"], "avg")]
    aC = [x * pm.get("ats", 1) for x in _dist(v["atsCC"], s["atsCC"], "avg")]
    aU = [x * pm.get("ats", 1) for x in _dist(v["atsUPI"], s["atsUPI"], "avg")]
    ip = [min(x * pm.get("intl", 1), 1) for x in _dist(v["intlPct"], s["intlPct"], "avg")]
    k = {key: [0.0] * n for key in ["cif", "sCC", "sUP", "xCC", "xUP", "tS", "tX", "iS", "cF"]}
    for m in range(n):
        prev = k["cif"][m - 1] if m > 0 else 0.0
        k["cif"][m] = max(0.0, prev + iss[m] - mA[m] * prev - mA[m] * iss[m])
        k["xCC"][m] = k["cif"][m] * acC[m] * tC[m]
        k["xUP"][m] = k["cif"][m] * acU[m] * tU[m]
        k["sCC"][m] = k["xCC"][m] * aC[m]
        k["sUP"][m] = k["xUP"][m] * aU[m]
        k["tS"][m] = k["sCC"][m] + k["sUP"][m]
        k["tX"][m] = k["xCC"][m] + k["xUP"][m]
        k["iS"][m] = k["tS"][m] * ip[m]
        k["cF"][m] = k["cif"][m] * v["cardFee"] if (m + 1) % 3 == 0 else 0.0
    k["derived_attrition"] = rates
    k["n"] = n
    return k


def calc_all(variants, cfg=None, volume_slabs=None, cif_slabs=None, pm=None):
    cfg = {**DEFAULT_CONFIG, **(cfg or {})}
    slV = volume_slabs or DEFAULT_VOLUME_SLABS
    slC = cif_slabs or DEFAULT_CIF_SLABS
    pm = pm or SCENARIOS["base"]
    vR = [calc_variant(copy.deepcopy(v), pm) for v in variants]
    mxM = max(v["years"] * 12 for v in variants)
    mxY = max(v["years"] for v in variants)
    keys = ["cif", "sCC", "sUP", "xCC", "xUP", "tS", "tX", "iS", "cF"]
    c = {key: [0.0] * mxM for key in keys}
    for vr in vR:
        for key in keys:
            for m in range(len(vr[key])):
                c[key][m] += vr[key][m]
    rV = [x * cfg["rvp"] for x in c["tS"]]
    rF = [x * cfg["rff"] for x in c["tX"]]
    iF = [x * cfg["ifp"] * cfg["intlRevShare"] for x in c["iS"]]
    rev_total = [rV[i] + rF[i] + c["cF"][i] + iF[i] for i in range(mxM)]
    sV = []
    for i, tx in enumerate(c["tX"]):
        sl = _slab(tx, slV)
        sV.append(sl["fb"] * tx + sl["pb"] * c["tS"][i])
    icF = [x * _slab(c["cif"][i], slC)["pb"] for i, x in enumerate(c["cF"])]
    iIS = [x * cfg["iip"] for x in c["iS"]]
    ms = [0.0] * mxM
    for y in range(mxY):
        s, e = y * 12, min(y * 12 + 12, mxM)
        if e <= s:
            continue
        y_cif = c["cif"][e - 1]
        y_s = sum(c["tS"][s:e])
        tgt = sum(v["cif"][y] if y < len(v["cif"]) else 0 for v in variants)
        hit = y_cif >= tgt * .95
        if cfg.get("milestone_rule") == "cif_spends":
            # Option from the blueprint; target spends must be supplied per year in cfg.
            tgt_s = (cfg.get("spend_targets") or [0] * mxY)[y]
            hit = hit and y_s >= tgt_s * .95
        if hit:
            bn = sum(c["cF"][s:e]) * cfg["mcb"] + y_s * cfg["msb"] + sum(c["iS"][s:e]) * cfg.get("imip", 0)
            for m in range(s, e):
                ms[m] = bn / (e - s)
    inc_total = [sV[i] + icF[i] + iIS[i] + ms[i] for i in range(mxM)]
    totS = sum(c["tS"])
    totR = sum(rev_total)
    totI = sum(inc_total) + cfg["upf"]
    netR = totR - totI
    bps = (lambda x: x / totS * 1e4 if totS > 0 else 0.0)
    years = []
    for y in range(mxY):
        s, e = y * 12, min(y * 12 + 12, mxM)
        sl = (lambda a: sum(a[s:e]))
        years.append({"year": f"Y{y + 1}", "cif": c["cif"][e - 1], "spends": sl(c["tS"]), "txns": sl(c["tX"]),
                      "intl_spends": sl(c["iS"]), "spends_cc": sl(c["sCC"]), "spends_upi": sl(c["sUP"]),
                      "revenue": sl(rev_total), "incentives": sl(inc_total),
                      "net": sl(rev_total) - sl(inc_total)})
    return {"total_spends": totS, "total_revenue": totR, "total_incentives": totI, "net_revenue": netR,
            "net_bps": bps(netR), "gross_bps": bps(totR), "incentive_bps": bps(totI),
            "corridor": {"floor": cfg["bpF"], "ceiling": cfg["bpC"]},
            "years": years, "monthly": {"cif": c["cif"], "spends": c["tS"], "revenue": rev_total,
                                         "incentives": inc_total},
            "variants": [{"name": v["name"], "derived_attrition": r["derived_attrition"]}
                         for v, r in zip(variants, vR)]}
