"""Insight ledger: every finding and every analyst verdict, as append-only JSON lines in the repo.
This is the platform's memory of what it has seen and how good its calls were.

  ledger/findings.jsonl   one evidence bundle per line
  ledger/verdicts.jsonl   {finding_id, verdict CORRECT|WRONG|PARTLY, true_cause, note, by, at}
"""
from __future__ import annotations

import datetime as dt
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Ledger:
    def __init__(self, folder=None):
        self.dir = Path(folder or ROOT / "ledger")
        self.dir.mkdir(parents=True, exist_ok=True)
        self.findings_path = self.dir / "findings.jsonl"
        self.verdicts_path = self.dir / "verdicts.jsonl"

    def _read(self, p):
        return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []

    def findings(self):
        return self._read(self.findings_path)

    def verdicts(self):
        return self._read(self.verdicts_path)

    def seen(self, finding_id):
        return any(f["finding_id"] == finding_id for f in self.findings())

    def add_finding(self, bundle):
        if self.seen(bundle["finding_id"]):
            return False
        with self.findings_path.open("a") as f:
            f.write(json.dumps(bundle, default=str) + "\n")
        return True

    def add_verdict(self, finding_id, verdict, true_cause=None, note="", by="analyst"):
        assert verdict in ("CORRECT", "WRONG", "PARTLY")
        rec = {"finding_id": finding_id, "verdict": verdict, "true_cause": true_cause, "note": note, "by": by,
               "at": dt.datetime.now().isoformat(timespec="seconds")}
        with self.verdicts_path.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        return rec

    def scorecard(self):
        """Precision by cause type and confidence. Input for the Learning workflow (W7)."""
        f_by_id = {f["finding_id"]: f for f in self.findings()}
        tally = defaultdict(Counter)
        for v in self.verdicts():
            f = f_by_id.get(v["finding_id"])
            if not f:
                continue
            b = f.get("best_explanation") or {}
            key = f"{b.get('type', 'UNEXPLAINED')}|{b.get('confidence', '-')}"
            tally[key][v["verdict"]] += 1
        out = {}
        for k, c in tally.items():
            n = sum(c.values())
            out[k] = {"n": n, "correct": c["CORRECT"], "partly": c["PARTLY"], "wrong": c["WRONG"],
                      "precision": round((c["CORRECT"] + 0.5 * c["PARTLY"]) / n, 2)}
        return out
