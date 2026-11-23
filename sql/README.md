# SQL for the semantic layer

Templates for the views the engines and agents read. Column names follow the observations in
`docs/reference/01_master_blueprint.md` section 4 and **must be verified in Phase 0** with
`python scripts/trino_probe.py describe <table>` before use. Placeholders in `{{ }}` are filled in
after discovery and recorded in `docs/PHASE0_CHECKLIST.md`.

If you cannot create views in Trino, the daily workflow runs these as queries and saves the results
as snapshot files; the engines then read the snapshots (`R360_SOURCE=local:<folder>`).

| File | Produces | Used by |
|---|---|---|
| `agg_weekly_issuer_merchant.sql` | weekly spend, txns, cards by issuer, card, merchant, category | Watcher, evidence tests, briefing |
| `txn_weekly_card_merchant.sql` | weekly spend per salted card key and merchant (never leaves Trino as raw rows; queried only inside aggregate queries) | Switching test |
