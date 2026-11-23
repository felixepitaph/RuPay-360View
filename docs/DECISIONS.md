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
Date: 2026-11-23. Reading npci/ainxt-enterprise showed external MCP servers are the native way to add tools (auto-registered as `<server>__<tool>`), and the HTTP tool path is HTTPS-only with private addresses blocked. Added `tools/mcp_server.py` (same 16 tools, same guards), `ainxt/skills_registry.json` (generated by `scripts/build_skill_registry.py`), (column refusal list: see D-018). `tools/server.py` stays as a fallback. Not verified against a running Buddy 2.0.1; see caveats in `ainxt/README.md` step 3.

### D-018: Column restrictions are not hard-coded; data team and internal models own them (Accepted, AK)
Date: 2026-11-23. AK: do not keep PII field restrictions at Claude's level; internal models set their own. Replaced the hard-coded sensitive-column list with `engine/config/restrictions.json` (empty by default; starter list in `restrictions.example.json`). Read-only SQL, row cap and the query log are unchanged. Risk accepted: with an empty list nothing in this code stops a query returning identifier columns, so enforcement depends on the Trino service account's permissions and AiNxt's own gates. Recommendation recorded: ask for a read-only account that cannot read raw PAN, mobile, email or account columns.


### D-019: Analysis catalogue of 61 analyses, 6 engines and 17 interactive modules (Proposed, AK)
Date: 2026-11-23. After comparing two HTML mockups, AK asked for the widest possible set of analyses and simulatable modules. `docs/ANALYSIS_CATALOGUE.md` lists them with the engine, data wave and required tests. Nothing is built. Each analysis needs a planted-truth test, a materiality floor and false-alarm control before it is shown. The internal models may reorder, merge or drop entries once the real Trino tables are known.

### D-020: Portfolio views are a design reference; internal data and documents override them (Proposed, AK)
Date: 2026-11-23. AK asked for a portfolio-first Command Center using the metrics he tracks (CIF, spends, volume, active cards, activation %, issuance, SPAC, TPAC, ATS), three channels (credit card, credit card on UPI, international), drill-downs (MCC, merchant, geography, UPI app), decline codes with reasons, new-to-ecosystem users, and card economics (interchange, switching fee, product fee). `scripts/portfolio_views.js` and `portfolio()` in `scripts/build_preview.py` implement these on synthetic data.

**Status: everything in these views is a starting point.** AK's internal data and reference documents take precedence wherever they differ, and the internal models should change the views, definitions and code without asking first (see D-016 and the discretion clause in AGENTS.md). Expect the following to be replaced:
- **Metric definitions.** CIF, active card, activation %, issuance, SPAC, TPAC and ATS are defined here from AK's one-line descriptions. Use the definitions in the internal documents and the actual Trino columns. "Active" is monthly and per channel here; the real window may differ. The all-channel active count here is a rough union of the three channels, not a true distinct count.
- **Channel definitions.** How a transaction is assigned to credit card, credit card on UPI or international, and what CIF means per channel (here the UPI and international CIF are subsets of the card base).
- **Economics.** Interchange, switching fee and product fee are placeholder numbers, not NPCI rates. Replace with the confidential rate tables. Which fee applies to which rail, whether product fee is per card per month, and who earns what are all assumptions to confirm. Rates stay out of committed files (AGENTS.md rule 4): load them from `docs/internal-context/`.
- **Decline codes.** The 12 codes and their descriptions are generic card-network codes. UPI has its own response codes. Replace the table with the internal reference document, including the cause grouping (technical, cardholder, issuer policy), which is mine.
- **New-user logic.** "New to the ecosystem" is first-ever transaction, per AK. The lag from issuance to first transaction and the first-transaction channel split are invented here.
- **Dimensions.** MCC list, merchant list, geographies and UPI app list are illustrative. Real lists come from the tables.
- **Layout, tiles and thresholds.** The scorecard targets, the spends bridge (CIF × activation × TPAC × ATS), the recovery and activation levers and the six-view structure are one way to organise it. Change them if what the data shows suggests a better one.
- **Visa and Mastercard.** Not shown. The views cover RuPay credit only, until a source for network comparison exists.

What stays regardless: numbers shown in a live version come from SQL or tested engines (the bridge arithmetic here is in the page and needs a parity test before it ships), and synthetic data never feeds real findings.
