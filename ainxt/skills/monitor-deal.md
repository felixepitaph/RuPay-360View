---
name: monitor-deal
description: Track an issuer deal against its locked baseline and flag cliffs.
---

# monitor-deal

Track an issuer deal against its locked baseline and flag cliffs.

## Steps
1. Load the deal's baseline variants and config (from the deal project file) and run `r360_deal_engine` for plan.
2. Load actuals by month with `r360_sql` (CIF, spends by rail, transactions) and run the engine again with actuals replacing plan months.
3. Report: deal-to-date net BPS (pro-rated and with full upfront), variance by driver, distance to next volume and CIF slab, milestone status (CIF >= 95% rule, or cif_spends if configured).
4. Re-forecast with the three approved modes (Hold plan, 3-month run-rate, manual) by calling the engine; never extrapolate yourself.
