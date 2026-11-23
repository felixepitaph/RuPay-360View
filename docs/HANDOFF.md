# Handoff (2026-11-23, after the full re-run)

> **Caveat from AK.** Everything here was built without access to Trino or the internal reference
> material. The internal AI models working on this repo will have both, and are free to change any
> part of the design, code, catalogs, agents or workflows on their own judgement when the data or
> documents call for it, then share the changes with AK (merge request + `docs/DECISIONS.md` entry +
> short summary). Only the data-safety rules in `AGENTS.md` stay fixed.

## 1. State
| Area | State |
|---|---|
| Design | `docs/ARCHITECTURE.md`: AiNxt harnesses + workflows over deterministic engines; learning through verdicts |
| Engines (`engine/r360/`) | Watcher, candidate causes, 3 evidence tests, investigation bundle, ledger + scorecard, briefing page, CVP-vs-MITC reconciler, Deal Model V1.1 (verified), read-only data access (Trino JWT or local DuckDB) |
| Tools | 16 tools (`tools/tool_specs.json`), HTTP server with bearer auth (`tools/server.py`), same functions via `python -m r360` |
| AiNxt definitions | 11 harnesses, 11 skills, 5 wikis, 8 workflows, scheduler tasks, Web Agent jobs (`ainxt/`) |
| Catalogs | YES: MITC v18, 11 cards (raw text), 12 live credit offers (headlines). IDFC: MITC, 11 cards (summaries), **123 offers (whole Nov booklet)**. 8 dated proposition events. 40 merchants. 54 watched sources |
| Demo | Synthetic data; pipeline finds the 3 planted moves correctly, including leaving one unexplained (`./demo/run_demo.sh`) |
| Tests | `python -m pytest`: 9 pass. `python scripts/validate_catalog.py`: all OK |

## 2. Your next steps, in order
1. Send `docs/QUESTIONS_FOR_AINXT_TEAM.md` (builder access, Trino token, tool registration).
2. Put the repo in Git (section 4) and open it in AiNxt Code.
3. Follow `ainxt/README.md` to set up the project, wikis, skills and the first four harnesses; test W1 on demo data in the Workflow preview.
4. With the Trino token: fill the `sql/` templates with the data team (Phase 0b), switch `R360_SOURCE=trino`.
5. Start marking findings Right / Partly / Wrong. That is the learning signal.

## 3. Open data items
- YES offer T&C PDFs (12) not read; Goibibo T&C link is dead. Web Agent job J2.
- IDFC card pages: re-extract from raw text (J3); 10 IDFC and 19 YES card pages not yet extracted.
- 4 CVP vs MITC conflicts to fix (`docs/RECONCILIATION_2026-11-23.md`).
- Network and BIN per card: from BIN data in Phase 0.
- IDFC booklet "UPI Offers" coupon codes contain "RUPAY": confirm whether RuPay-funded.

## 4. Putting this in Git (no command line)
1. Unzip; you get `rupay-360-platform`.
2. Create a **private** repository named `rupay-360` in the Git host AiNxt uses (GitHub: felixepitaph/RuPay-360View).
3. Use the web "Upload files" option; drag in everything inside the folder; commit to `main`.
4. Check `.gitignore` arrived (hidden files can be skipped; create it by hand if so).
5. Never upload `.env`, confidential documents or data files.
Then in AiNxt: Code > Clone from Git with that URL.

## 5. Working with your internal Claude
First message in AiNxt Code (or a harness test):
> Read AGENTS.md, docs/HANDOFF.md and docs/ARCHITECTURE.md. Then do <one item from section 2 or 3>. Use only the inputs I attach. Get numbers only from tools, cite every source, run `python -m pytest` and `python scripts/validate_catalog.py` before finishing, and list anything you were unsure about.
