"""Watcher: finds unusual weekly moves. Plain statistics, no model, same data -> same flags.

Input: DataFrame `merchant_weekly` with columns
  week_start (date), issuer_bank, merchant_id, spend, [txns], [cards]
Method per (issuer_bank, merchant_id) series:
  expected = median of the previous `baseline_weeks` weeks (seasonally adjusted with last year's
  same-week ratio when 60+ weeks of history exist); spread = MAD of log spend over the same weeks.
  Flag when |robust z| >= z_threshold AND |pct change| >= min_abs_pct_change.
Context checks attached to every flag (the Critic uses them):
  issuer_wide   - most merchants of the same issuer moved the same way that week (portfolio or data issue)
  partial_week  - total rows / cards that week far below normal (late or incomplete data)
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

CFG_PATH = Path(__file__).resolve().parents[1] / "config" / "watcher.json"


def load_config(path=None):
    return json.loads(Path(path or CFG_PATH).read_text())


def scan(df: pd.DataFrame, cfg: dict | None = None, weeks: list | None = None) -> list[dict]:
    cfg = cfg or load_config()
    df = df.copy()
    df["week_start"] = pd.to_datetime(df["week_start"]).dt.date
    g = df.groupby(["issuer_bank", "merchant_id", "week_start"], as_index=False)["spend"].sum()
    all_weeks = sorted(g["week_start"].unique())
    targets = weeks or all_weeks[-1:]
    B = cfg["baseline_weeks"]
    flags = []
    for (iss, mid), s in g.groupby(["issuer_bank", "merchant_id"]):
        s = s.set_index("week_start")["spend"].reindex(all_weeks).fillna(0.0)
        for wk in targets:
            if wk not in s.index:
                continue
            i = all_weeks.index(wk)
            hist = s.iloc[max(0, i - B):i]
            if len(hist) < cfg["min_history_weeks"] or hist.median() < cfg["min_baseline_spend_inr"]:
                continue
            expected = float(hist.median())
            if i >= 52 + B:  # seasonal adjustment from last year, if available
                ly = s.iloc[i - 52]
                ly_base = s.iloc[i - 52 - B:i - 52].median()
                if ly_base > 0 and ly > 0:
                    expected *= float(ly / ly_base)
            actual = float(s.iloc[i])
            logs = np.log(hist.clip(lower=1.0))
            mad = float(np.median(np.abs(logs - np.median(logs)))) * 1.4826 or 0.02
            z = (np.log(max(actual, 1.0)) - np.log(max(expected, 1.0))) / max(mad, 0.02)
            pct = actual / expected - 1 if expected else 0.0
            if abs(z) >= cfg["z_threshold"] and abs(pct) >= cfg["min_abs_pct_change"]:
                fid = hashlib.sha1(f"{iss}|{mid}|{wk}".encode()).hexdigest()[:10]
                flags.append({"flag_id": f"F-{fid}", "issuer_bank": iss, "merchant_id": mid,
                              "week_start": str(wk), "actual_spend": round(actual, 2),
                              "expected_spend": round(expected, 2), "pct_change": round(pct, 4),
                              "robust_z": round(float(z), 2), "direction": "DROP" if pct < 0 else "RISE",
                              "baseline_weeks": B, "watcher_version": cfg.get("version")})
    _context(flags, g, df, cfg)
    return sorted(flags, key=lambda f: f["pct_change"])


def _context(flags, g, df, cfg):
    if not flags:
        return
    B = cfg["baseline_weeks"]
    weeks = sorted(g["week_start"].unique())
    for f in flags:
        wk = pd.to_datetime(f["week_start"]).date()
        i = weeks.index(wk)
        prev = weeks[max(0, i - B):i]
        same = g[g.issuer_bank == f["issuer_bank"]]
        piv = same.pivot_table(index="merchant_id", columns="week_start", values="spend", aggfunc="sum").fillna(0)
        if prev:
            chg = piv[wk] / piv[prev].median(axis=1).replace(0, np.nan) - 1
            chg = chg.dropna()
            moved = (np.sign(chg) == np.sign(f["pct_change"])) & (chg.abs() >= cfg["min_abs_pct_change"])
            f["issuer_wide_share"] = round(float(moved.mean()), 2) if len(chg) else None
            f["issuer_wide"] = bool(len(chg) >= 4 and moved.mean() >= cfg["issuer_wide_share"])
        col = "cards" if "cards" in df.columns else "spend"
        tot = df[df.issuer_bank == f["issuer_bank"]].groupby("week_start")[col].sum()
        if prev and tot.get(wk) is not None:
            ratio = float(tot[wk] / tot[prev].median()) if tot[prev].median() else 1.0
            f["volume_ratio_vs_normal"] = round(ratio, 2)
            f["partial_week"] = ratio < cfg["partial_week_ratio"]
