# RuPay 360° Network Portfolio Intelligence

Internal platform that finds and explains moves in YES BANK and IDFC FIRST card spend by tying them to
what each card promises (**CVP**), charges or restricts (**MITC**) and subsidises (**offers**), and gets
better as analysts correct it. Agents run on the internal **AiNxt** platform.

**Start here:** `docs/HANDOFF.md` (state, next steps) and `docs/ARCHITECTURE.md` (how it works).

## Try it in two minutes (synthetic data)
```bash
pip install -r requirements.txt
python -m pytest            # deal engine, insight pipeline, safety guards
./demo/run_demo.sh          # builds synthetic data, finds 3 planted moves, writes app/briefing_demo.html
```

## Where things are
| Path | What |
|---|---|
| `AGENTS.md` | Rules for any AI working in this repo. **Read first.** |
| `docs/ARCHITECTURE.md` | Design: layers, intelligence loop, where agents help, where state lives |
| `docs/HANDOFF.md` | Current state, open items, how to upload and continue |
| `docs/PHASES.md` | Roadmap with "done when" tests |
| `docs/REVIEW_INPUTS.md` | Review of all inputs (blueprint, mockups, deal model, documents, AiNxt) |
| `docs/RECONCILIATION_2026-11-23.md` | Web CVP vs MITC conflicts |
| `docs/QUESTIONS_FOR_AINXT_TEAM.md` | What to ask before deploying agents |
| `ainxt/` | Paste-ready AiNxt harnesses, skills, wikis, workflows, scheduler tasks, Web Agent jobs |
| `engine/r360/` | Deterministic engines: watcher, causes, evidence tests, deal engine, ledger, briefing, tools |
| `tools/` | Tool specs (`tool_specs.json`) and HTTP tool server for AiNxt |
| `catalog/` | CVP, MITC, offers, proposition events, merchant master, watched sources (all with sources) |
| `schemas/` | JSON schemas for every catalog file |
| `sql/` | Semantic-layer SQL templates (verify column names in Phase 0) |
| `ledger/` | Findings and analyst verdicts (the platform's memory) |
| `proposals/` | Agent proposals awaiting approval |
| `demo/` | Synthetic data generator, demo catalog, demo script |
| `tests/` | Automated checks |
| `scripts/` | Trino probe and catalog validator |
| `docs/internal-context/` | Confidential documents (git-ignored) |
