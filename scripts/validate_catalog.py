#!/usr/bin/env python3
"""Validate catalog JSON files against schemas/.

Usage: python scripts/validate_catalog.py            (checks catalog/ and schemas/examples/)
File name decides the schema: cvp_*.json, mitc_*.json, offers_*.json
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = {
    "cvp": ROOT / "schemas/cvp_catalog.schema.json",
    "mitc": ROOT / "schemas/mitc_catalog.schema.json",
    "offers": ROOT / "schemas/offers_catalog.schema.json",
    "proposition": ROOT / "schemas/events_catalog.schema.json",
}
REFERENCE = {"merchant_master.json", "registry.json"}  # reference files, checked for valid JSON only


def main() -> int:
    failures = 0
    files = sorted(list((ROOT / "catalog").rglob("*.json")) + list((ROOT / "schemas/examples").glob("*.json")))
    for f in files:
        kind = f.name.split("_")[0]
        if f.name in REFERENCE:
            json.loads(f.read_text())
            print(f"OK    {f.relative_to(ROOT)} (reference, JSON only)")
            continue
        if kind not in SCHEMAS:
            print(f"SKIP  {f.relative_to(ROOT)} (name must start with cvp_, mitc_ or offers_)")
            continue
        schema = json.loads(SCHEMAS[kind].read_text())
        data = json.loads(f.read_text())
        items = data if isinstance(data, list) else [data]
        errors = [e for item in items for e in Draft7Validator(schema).iter_errors(item)]
        if errors:
            failures += 1
            print(f"FAIL  {f.relative_to(ROOT)}")
            for e in errors:
                print(f"      {'/'.join(map(str, e.path)) or '(root)'}: {e.message}")
        else:
            print(f"OK    {f.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
