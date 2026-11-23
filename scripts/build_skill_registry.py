#!/usr/bin/env python3
"""Builds ainxt/skills_registry.json: one AiNxt SkillDefinition per markdown skill in ainxt/skills/.

AiNxt's skill registry (mcp/skill_registry.py in npci/ainxt-enterprise) describes a skill by
name, description, ordered tools, tags, version. The tools are listed in the order they are first
mentioned in the skill's Steps. Tool names carry the "rupay360__" prefix AiNxt adds to tools
from an external MCP server named "rupay360". If you register the server under another name,
pass --server-name.
Run:  python scripts/build_skill_registry.py [--server-name rupay360]
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
from r360.tools import FUNCS  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--server-name", default="rupay360")
a = ap.parse_args()

out = []
for f in sorted((ROOT / "ainxt" / "skills").glob("*.md")):
    text = f.read_text()
    m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---", text)
    assert m, f"{f.name}: missing name/description front matter"
    order = []
    for t in re.findall(r"`(r360_[a-z_]+)`", text):
        if t in FUNCS and t not in order:
            order.append(t)
        elif t not in FUNCS:
            sys.exit(f"{f.name}: references unknown tool {t}")
    out.append({"name": m.group(1).replace("-", "_"), "description": m.group(2).strip(),
                "tools": [f"{a.server_name}__{t}" for t in order], "workflow_name": None,
                "tags": ["rupay360"], "version": "1.0.0", "author": "rupay-360", "enabled": True,
                "instructions_file": f"ainxt/skills/{f.name}"})
(ROOT / "ainxt" / "skills_registry.json").write_text(json.dumps(out, indent=2) + "\n")
print(f"wrote ainxt/skills_registry.json ({len(out)} skills)")
