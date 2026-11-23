# Wiki: metric-dictionary

The authoritative list is `docs/METRIC_DICTIONARY.md` in the repo; this wiki mirrors it for agents.
Agents may invent new metrics during an investigation (write the SQL, run it, quote it). A metric
becomes part of this dictionary only through `r360_propose_metric` and approval in the Curator Queue.

| Metric | Definition | Status |
|---|---|---|
| Spend (GMV) | Sum of approved transaction amount | To confirm in Phase 0 |
| Active cards (30D) | Distinct cards with an approved transaction in 30 days | To confirm |
| ATS / TPAC / SPAC | GMV / txns; txns / active cards; GMV / active cards | To confirm |
| Recapture share | (cohort spend gained at competitor) / (cohort spend lost at flagged merchant), flagged week vs 8-week baseline | Engine (evidence.py) |
| DiD change | (treated change) - (control change), flagged week vs 8-week baseline | Engine (evidence.py) |
| Robust z (Watcher) | log(actual) - log(expected) over 1.4826 x MAD of 8-week log spend | Engine (watcher.py) |
| Net BPS | Net revenue / spends x 10,000 | Engine (deal_engine.py) |
