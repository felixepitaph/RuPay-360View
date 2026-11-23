# Roadmap (re-sequenced around AiNxt, 2026-11-23)

Scope: YES BANK and IDFC FIRST. A phase is done only when its "done when" test passes.

| Phase | What | Done when | State |
|---|---|---|---|
| **0a. Access** | AiNxt builder rights; read-only Trino JWT in API Token Vault; tool registration method; Git host confirmed | `python -m r360 sql "SELECT 1"` works with `R360_SOURCE=trino` from the tool host | Waiting on AiNxt / data team |
| **0b. Semantic layer** | Fill `sql/` templates; `dim_card_bin_master` (BINs for YES and IDFC), `dim_merchant_master`; 5 discovery gaps | `agg_weekly_issuer_merchant` returns last 10 weeks and matches a trusted Superset number within 1% | Templates ready |
| **1. Insight loop live** | Harnesses 01, 02, 03, 11 + W1 + Scheduler; briefing page | 4 consecutive daily runs; at least 10 analyst verdicts recorded | Engines, tools, demo, harness files ready |
| **2. Catalog loop live** | Harnesses 04, 05 + Web Agent jobs + W2; remaining cards; YES T&C PDFs | One real page change detected, extracted and approved end to end | Catalogs: YES 11 cards, IDFC 11 cards, 123 IDFC + 12 YES offers |
| **3. Proposition impact** | Harness 06 + W3; events catalog grows with each approved change | D+30 impact measured for 3 events, each with a control group | Events seed (8) ready |
| **4. Learning loop** | Harness 09 + W7 + W6 digest | First approved threshold or playbook change from the scorecard | Ledger and scorecard ready |
| **5. App modules** | Command Center, Card Economics, Wallet Share, Proposition Hub, Deal Performance (Gemini V2 layout) each with a "why did this move" panel | Each module reads snapshots and the ledger; numbers reconcile with Superset | Briefing page built |
| **6. Deal performance** | Deal Monitor (W4); Part B (baselines, actuals, re-forecast) on internal storage | Actuals for one deal tracked monthly | Engine ported and verified |
| **7. Pitch packs and Copilot** | Harnesses 08, 10 | One issuer evidence pack used in a real meeting | Harness files ready |

New flag types to add after Phase 1 (same pipeline): wallet migration, acceptance leakage (decline clusters), near-cliff users, deal slab proximity.
