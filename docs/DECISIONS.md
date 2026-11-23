# Decision log

Add an entry whenever a choice is made or something found in the data or documents differs from `docs/reference/`.

Template:
```
### D-00X: title
Date: | Author: | Status: Proposed / Accepted
Source: document or table that informed it
Change: what is different from the reference docs
Affects: files, schemas, modules
Check: test or reconciliation that confirms it
```

### D-001: Scope limited to YES Bank and IDFC FIRST (Accepted)
Documents for these two banks can be obtained directly. All modules are kept, each implemented for these issuers first.

### D-002: Direct read-only Trino access, snapshot architecture (Accepted)
A scheduled job runs reviewed SQL and saves aggregates to `data/`. The app reads those files. Nothing in the UI queries Trino live. If scratch tables can be created later, aggregates may move into Trino.

### D-003: Models never compute figures (Accepted)
Metrics come from SQL or tested code. Models extract documents and write explanations only.

### D-004: Catalog changes are approved by merging a pull request (Accepted)
Each change carries its source document. Merging is the human sign-off and the audit trail.

### D-005: Deal data stays on internal infrastructure (Proposed)
Deal Model V1.1 used a cloud Supabase project. Commercial terms with banks should be stored on internal systems. Confirm with IT/compliance.

### D-007: MITC and offers schemas revised after first real documents (Accepted)
Date: 2026-11-23. Source: YES MITC v18, IDFC MITC, IDFC Nov 2026 offers booklet.
Change: MITC is now one file per issuer with variant-keyed rule tables (not one per card). Offers gained `eligible_cards` (names as printed), `channel`, `days_of_week`, `payment_mode: ANY` and `extraction_confidence`. See `docs/EXTRACTION_FINDINGS.md`.
Affects: `schemas/mitc_catalog.schema.json`, `schemas/offers_catalog.schema.json`, `catalog/`.
Check: `python scripts/validate_catalog.py` passes on all catalog files.

### D-006: Mockup is a UI reference only (Accepted)
`docs/reference/ui_mockup_v2_gemini_FAKE_DATA.html` contains hardcoded dummy data. Its deal engine reproduced the V1.1 single-variant reference (15.996 / 24.05 / 13.47 bps) but multi-variant logic must be ported from the original V1.1 `App.jsx`.

### D-008: AiNxt is the agent and orchestration layer (Accepted)
Date: 2026-11-23. Source: screenshots of AiNxt Buddy 2.0.1.
Change: Agents are AiNxt Factory harnesses; Workflows chain them; Scheduler triggers them; Curator Queue holds approvals; Web Agent does scraping; Code agent / ADLC Pipeline change the repo. The repo provides engines, tools, catalogs and paste-ready AiNxt definitions (`ainxt/`).
Affects: docs/ARCHITECTURE.md, ainxt/, tools/.

### D-009: Agents may invent metrics and tests; arithmetic stays in SQL and engines (Accepted, supersedes the wording of D-003)
Agents design analyses and write SQL; tools execute it; results are quoted with their SQL. New metrics become permanent through `r360_propose_metric`.

### D-010: Deal Model V1.1 engine ported to Python (Accepted)
`engine/r360/deal_engine.py`, line-for-line from App.jsx. Matches blueprint reference: closing CIF, derived attrition, totals, 15.996 / 24.05 / 13.47 net BPS (`tests/test_deal_engine.py`). Added optional `cif_spends` milestone rule, default unchanged.

### D-011: Learning without training (Accepted)
Findings and verdicts in `ledger/`; scorecard by cause type; Learning Steward proposes threshold, prior and playbook changes. Nothing is fine-tuned.

### D-012: Trino via read-only JWT; DuckDB for local snapshots and demo (Accepted)
`data_access.py` supports JWT (AiNxt requirement) and password; the same SQL runs on local snapshot files through DuckDB.

### D-013: Git host is GitHub (Accepted, AK)
Repo: github.com/felixepitaph/RuPay-360View for now; possibly the NPCI organisation (github.com/npci) later. AiNxt Code's clone dialog asks for a GitLab token: confirm with the AiNxt team that it can clone from GitHub (question 5).

### D-014: App hosting assumed a small internal web app (Proposed)
The app only reads files (snapshots, catalogs, ledger). First screen: Insight Briefing. Confirm hosting; fallback is the briefing page plus AiNxt chat plus Superset.

### D-015: IDFC offers booklet fully extracted; offers dated with page-level provenance (Accepted)
All 123 offers from pages 3-22 of the Nov 2026 booklet. Pages 6-20 carry an "EMI transactions only" header; offers there are `payment_mode: EMI` unless marked Full Swipe. Merchant names came from logos (read visually), MakeMyTrip and Goibibo rows MEDIUM confidence.

### D-016: Internal models may redesign on their own judgement (Accepted, AK)
Date: 2026-11-23. Internal models with Trino and the internal reference material may change any part of the design, code, catalogs, agents or workflows when evidence calls for it, and share each change with AK (merge request, decision entry, summary). Data-safety rules in AGENTS.md stay fixed.

### D-017: Tools are exposed as an MCP stdio server (Proposed, pending AiNxt confirmation)
Date: 2026-11-23. Reading npci/ainxt-enterprise showed external MCP servers are the native way to add tools (auto-registered as `<server>__<tool>`), and the HTTP tool path is HTTPS-only with private addresses blocked. Added `tools/mcp_server.py` (same 16 tools, same guards), `ainxt/skills_registry.json` (generated by `scripts/build_skill_registry.py`), and widened the sensitive-column refusal list to match AiNxt's own database server. `tools/server.py` stays as a fallback. Not verified against a running Buddy 2.0.1; see caveats in `ainxt/README.md` step 3.

