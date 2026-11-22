# Architecture Decision Record (ADR) Log — RuPay 360° Platform

> **Governance Rule for Internal Claude & ChatGPT Models:**
> Whenever internal confidential documents (`/docs/internal-context/`) or live Trino schema discovery reveal richer fields, sharper regulatory rules, or superior architecture than what is outlined in the baseline blueprint, **you are authorized and expected to upgrade the platform—and you MUST append a concise ADR entry below.**

---

## Locked Baseline Decisions

### ADR-001 — Proposition-Bound Causal Architecture
* **Date:** 2026-11-23 | **Status:** Accepted
* **Decision:** Treat CVP, MITC, and Offers (`FS` vs. `EMI`) as the **causal control plane** binding all telemetry, economics, wallet share, and commercial deal views—never as a standalone consumer aggregator directory.
* **Consequence:** Every qualitative update must be versioned with `effective_from` timestamps and joined via `card_id`, `mcc`, and `merchant_id` into telemetry overlays and DiD attribution engines.

### ADR-002 — Strict Workspace Filter Isolation & Collapsible Shell
* **Date:** 2026-11-23 | **Status:** Accepted
* **Decision:** The persistent 3-tier Global Context Filter Bar applies **strictly to Workspace 1 (`Command Center`, `Card Economics`, `Wallet Share`)**. `Proposition Hub` (Workspace 2) holds its own page-level cross-network filter bar; `Deal Performance` (Workspace 3) is scoped strictly by its Deal Project Switcher and Role toggle (`Network A` / `Issuer B`). Left navigation must collapse to an icon-only rail.
* **Consequence:** Prevents global Trino filters from breaking cross-network Visa/Mastercard comparisons or polluting commercial deal simulations.

### ADR-003 — Centralized 6- vs. 8-Digit BIN Normalization & Collateral Tagging
* **Date:** 2026-11-23 | **Status:** Accepted
* **Decision:** Prohibit inline `CASE WHEN SUBSTR(payerbin...)` truncation inside tab SQL. Centralize all BIN matching, `Secured (FD-Backed)` vs. `Unsecured` flags, `Proprietary` vs. `Co-Brand (Discretionary / Non-Discretionary)` attributes, and `is_virtual_floater` flags inside `dim_card_bin_master`.
* **Consequence:** Guarantees 100% reconciliation across Command Center, Card Economics, Wallet Share, and Deal Performance actuals.

### ADR-004 — Deal Model V1.1 Engine Fidelity & Part B Rules
* **Date:** 2026-11-23 | **Status:** Accepted
* **Decision:** Port Deal Model V1.1 directly from GitHub source into a pure, UI-free TypeScript module (`packages/deal-engine`) verified by automated CI tests against all Section 11 reference benchmarks (`15.996` Base Net BPS, `24.05` Conservative, `13.47` Aggressive, `0.000%`–`5.161%` derived attrition). Keep both Milestone rules (`cif` default and `cif_spends` selectable), display **both** pro-rated and full upfront Deal-to-Date BPS side-by-side, and fix V1.1's hard-coded `"Int'l (25%)"` label and dead `monthlyAttrition` field.
* **Consequence:** Zero formula drift across monthly token cycles; full 6-sub-tab parity without shortcuts.

### ADR-005 — Confidential Interchange & Pricing Isolation
* **Date:** 2026-11-23 | **Status:** Accepted
* **Decision:** Isolate all Card & UPI 2×2 interchange rate tables behind `schemas/interchange_rules.schema.json`. Seed with clearly labelled `[DUMMY PLACEHOLDER RULES]` during external scaffolding and swap with actual confidential internal rate schedules from `/docs/internal-context/` during internal Phase 0 deployment.
* **Consequence:** Preserves confidentiality while keeping the SQL and UI economics engine 100% ready for real rates.

---

## Template for Internal Model Upgrades (Append Below)

```markdown
### ADR-00X — [Short Descriptive Title]
* **Date:** YYYY-MM-DD | **Author:** [Claude / ChatGPT + Reviewer] | **Status:** Proposed / Accepted
* **Triggering Source:** [Internal Document Name in `/docs/internal-context/` OR Trino Table Discovered]
* **What Changed from Baseline Blueprint:** [Concise delta]
* **Affected Packages / Schemas:** [e.g., `packages/trino-sql`, `apps/tab-economics`, `02_Trino_Semantic_Layer.md`]
* **Verification / Tests Updated:** [Unit test or SQL reconciliation check confirming accuracy]
```