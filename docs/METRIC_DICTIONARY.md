# Metric dictionary

Every number in the app must match a definition here. Fill in once, confirm with your team, then treat as fixed.
Change a definition only through a `DECISIONS.md` entry.

| Metric | Definition (fill in) | Source table.column | Notes |
|---|---|---|---|
| Cards in Force (CIF) | | | Open cards at month end? |
| Active card (30D) | Distinct cards with at least 1 approved transaction in last 30 days? | | Which transaction types count? |
| Active rate | Active cards / CIF | | |
| GMV | Sum of approved transaction amount | | Rupees or crore? Include reversals? |
| ATS | GMV / approved transactions | | |
| TPAC | Approved transactions / active cards | | |
| SPAC | GMV / active cards | | |
| ASR (approval success rate) | Approved / total attempts | | |
| Monthly user spend slab | Total spend of a card across rails in a month, bucketed | | Slab edges: <5K, 5K-15K, 15K-50K, 50K-1L, 1L-2.5L, >2.5L |
| Ticket-size slab | Per-transaction bucket | | Edges in `docs/reference/03_trino_semantic_layer.md` |
| Realized interchange yield | | | Needs fee fields (Gap 5) |
| Net BPS (deal) | Net revenue / total spends x 10,000 | | Reference: 15.996 on default case |
| Recapture share (engine) | Competitor spend gained / flagged-merchant spend lost, for the flagged merchant's baseline cardholders | txn_weekly_card_merchant | `engine/r360/evidence.py` |
| DiD change (engine) | Change for offer-eligible issuer's cards minus change for other issuers, flagged week vs 8-week baseline | agg_weekly_issuer_merchant | `engine/r360/evidence.py` |
| Robust z (engine) | (log actual - log expected) / (1.4826 x MAD of 8 weeks of log spend) | agg_weekly_issuer_merchant | `engine/r360/watcher.py`, thresholds in `engine/config/watcher.json` |
