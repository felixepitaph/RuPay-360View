# AGENTS.md: rules for AI models working in this repo (AiNxt Code agent, ADLC Pipeline, harnesses)

Read this file, `docs/HANDOFF.md`, `docs/ARCHITECTURE.md` and `docs/DECISIONS.md` at the start of every session.

## Scope
- Banks: **YES BANK and IDFC FIRST Bank.** Networks: RuPay, Visa, Mastercard. Other issuers only as controls.
- Work only on the task or Jira ticket named. Do not start later phases.

## Discretion clause (from AK, 2026-11-23)
This repo was designed without access to Trino or the internal reference material. You (the internal
AI models) will have both: live Trino and the documents AK uploads to `docs/internal-context/`.
**You are free to change any part of this design on your own judgement** when what you find there
shows a better way: the architecture, engines and thresholds, SQL, schemas, catalogs, metrics, the
AiNxt harnesses, skills, wikis and workflows, the roadmap, and these instructions themselves.

When you do:
1. Make the change on a branch and open a merge request; do not wait for permission to propose it.
2. Add a `docs/DECISIONS.md` entry: what changed, what you found (table, column or document) that
   justified it, and what it replaces.
3. Share a short summary with AK: what changed, why, how you tested it, and anything AK must decide.

What stays fixed regardless (these protect the data and the people in it, not the design):
read-only data access, no credentials or personal data in outputs or commits, confidential terms
kept out of committed files, a source for every catalog value, and tests for any change to the
maths (update the tests with the change and explain the difference).

## Hard rules
1. **Numbers come from SQL or tested engines.** You may invent metrics and tests; write the SQL or code, run it, quote the result. Never do the arithmetic in prose. Math in `engine/` needs tests first (`tests/`).
2. **Read-only data.** All queries go through `engine/r360/data_access.py` (read-only, no personal-data columns, row cap, logged). Never bypass it.
3. **No secrets in the repo.** Tokens live in `.env` or the AiNxt API Token Vault. Never print or commit credentials, PAN, card keys, mobile numbers or raw transaction rows.
4. **Confidential documents** stay in `docs/internal-context/` (git-ignored). Do not copy interchange rates or deal terms into committed files.
5. **Every catalog value needs a source** (document or URL, page or section, date retrieved). Unknown = null + flag. MITC wins on fees.
6. **Agents propose, people approve.** Harnesses write only to `proposals/` and (via the pipeline) `ledger/findings.jsonl`. Catalogs, `engine/config/`, wikis and metric definitions change only through an approved proposal or a reviewed merge.
7. **Never change verified maths silently.** `engine/r360/deal_engine.py` must keep passing `tests/test_deal_engine.py` (15.996 / 24.05 / 13.47 bps). Any change needs a `docs/DECISIONS.md` entry.
8. **Never guess a schema.** Use `scripts/trino_probe.py describe` and record findings in `docs/PHASE0_CHECKLIST.md`.
9. **Mockup and demo data are fake.** `docs/reference/*FAKE_DATA*` and `demo/` must never feed real findings.

## Before finishing any change
`python -m pytest` and `python scripts/validate_catalog.py` must pass. Summarise: files changed, tests run, open questions.

## Git workflow
Branch per task (`phase-N-short-name` or the Jira key), small commits, merge request with what/why/how tested. Never push to `main`.
