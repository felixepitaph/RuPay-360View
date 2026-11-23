# Analysis catalogue (proposed, 2026-11-23)

Status: PROPOSED by AK's ideation session. Nothing here is built. Internal models may add, merge or drop entries under the discretion clause in `AGENTS.md`; record each change in `docs/DECISIONS.md`. A readable version with interactive-module detail lives in the Claude Doc "RuPay 360: Analysis Catalogue and Interactive Modules".

Frame: every screen answers one of five decisions: (1) where are we winning or losing, (2) why (cause + evidence + confidence), (3) what next (forecast with range), (4) what to propose to the issuer, (5) did it work and was the platform right.

## Waves (what each analysis needs)
- **W0** catalog files only (available now)
- **W1** aggregate Trino tables (needs Phase 0b table and column names, MITC thresholds, offer dates)
- **W2** encrypted customer ID (must be stable across card and UPI) + BIN-to-variant mapping
- **W3** confidential reference documents (rate tables, deal terms, issuer priors) in `docs/internal-context/`

Wallet share means NPCI-visible spend only: the same customer's card spend versus UPI-from-savings spend. It excludes Visa and Mastercard.

## Engines (each is tested code or a tested SQL template)
| Code | Engine | Method |
|---|---|---|
| E1 | Event study | Before/after against a control or synthetic control, with a band |
| E2 | Bunching | Distribution around a gate: excess mass above, missing mass below |
| E3 | Cohort and survival | Retention and activity curves by cohort, with bands |
| E4 | Flow and substitution | Per-customer before/after across merchants, rails, cards; recapture share |
| E5 | Decomposition | Price-volume-mix split of a ratio change (net bps) |
| E6 | Elasticity | Behaviour difference per unit of benefit (holders vs non-holders, before vs after) |
| Deal | Deal Model | Existing tested engine (15.996 / 24.05 / 13.47 bps) |

## Required of every analysis
1. A planted-truth test on synthetic data (known effect must be found) before it goes live.
2. A materiality floor and a multiple-testing correction; not a bare z-score.
3. Ranges and an evidence-strength badge on any forecast or simulator output; say so when no past events resemble the design.
4. Provenance on every number: source table, freshness, row count, real or synthetic.
5. Numbers from SQL or tested engines; agents propose new analyses through `r360_propose_metric`, people approve.

## Analyses (ID, name, engine, wave, question)
### A. Benefits and behaviour
- A1 Decorative-benefit audit, E6, W1: which catalog benefits cost money but change no behaviour (lounge to travel, fuel waiver to fuel, forex to international, EMI to durables)?
- A2 Bunching at thresholds, E2, W2: do fee-waiver, milestone and lounge gates steer spend; does spend drop after the gate is earned?
- A3 Cap-hit analysis, E2, W2: share hitting a monthly reward cap and what they do next.
- A4 Fee elasticity, E6, W2: retention and spend of fee-waived versus fee-paying customers.
- A5 Welcome-benefit payback, E3, W2: months until a welcome benefit pays back in spend.
- A6 Reward-rationality gap, E6, W0+W2: best effective rate per category versus where spend goes.

### B. Customer structure
- B1 Wallet share, E4, W2: card versus UPI-from-savings share for the same customer.
- B2 Net-new versus substitution, E4, W2.
- B3 Archetypes, E3, W2: behaviour segments and each BIN's mix shift.
- B4 Autopilot spend, E3, W2: recurring (sticky) versus promotion-driven (rented).
- B5 Gateway merchant, E3, W2: first merchant that predicts long-term default use.
- B6 Category breadth, E3, W2: does breadth predict retention?
- B7 Graduation ladders, E3, W2: slab moves, triggers, FD-backed to unsecured timing.
- B8 Reactivation triggers, E1+E3, W2.
- B9 Intra-RuPay card wars, E4, W2: which of two RuPay cards wins each category.
- B10 90-day survival, E3, W2: drop-offs at day 31, 61, 91 by variant and welcome offer.
- B11 BIN health score, E3, W2: early warning from velocity and breadth decay.
- B12 Activation headroom, E4, W2: by archetype, cards and spend at stake.

### C. Rails and friction
- C1 Rail migration, E4+E5, W2+W3: POS to UPI-credit shift and its effect on net bps.
- C2 Failure rupees at stake, E4, W1: spend lost to technical declines; retried or switched share.
- C3 Outage resilience, E1, W1: recovery by hour and rail.
- C4 Acceptance gap, E4, W1: high UPI volume, low credit-on-UPI share merchants.
- C5 Ticket cliff at Rs2K, E2, W1: zero-MDR boundary effect on ticket size and failures.
- C6 Offer timing, E1, W1: best hour or weekday.
- C7 Lead-lag, E1, W1: rails or categories that move first.

### D. Offers and competition
- D1 Pull-forward versus net-new, E1, W1.
- D2 Offer fatigue, E1, W1.
- D3 Competitor-response map, E4, W1.
- D4 Substitution graph, E4, W1: accumulates edges from every finding.
- D5 Funder effectiveness, E1, W3: lift per rupee by issuer, merchant or network funding.
- D6 Co-brand partner dependence, E4, W1.
- D7 Offer calendar collisions, E1, W0.
- D8 Offer whitespace, E4, W0+W1.
- D9 Merchant concentration, E5, W1.
- D10 Halo effect, E1, W1.

### E. Time and events
- T1 Event study library, E1, W1: typical effect per event kind; becomes priors.
- T2 Calendar effects, E1, W1: festival, salary day, month-end, IPL.
- T3 Regulatory radar, E1, W1.
- T4 Time machine, platform, W1: findings as of a past date.

### F. Commercial and deal
- F1 Price-volume-mix waterfall, E5, W3.
- F2 Incentive efficiency frontier, E5, W3.
- F3 Renewal readiness, Deal, W3.
- F4 Revenue at risk, E1+E5, W1+W3.
- F5 Network revenue concentration, E5, W3.
- F6 Unit economics per BIN, E5, W3.
- F7 Deal fan charts (P10/P50/P90), Deal, W3.
- F8 Cliff-crossing probability, Deal, W3.
- F9 Devaluation-risk radar, E6, W3: HYPOTHESIS; test against the dated events before showing.
- F10 Peer benchmark, E4+E5, W2+W3.
- F11 Volume not to chase, Deal, W3: where extra volume lowers net revenue because of cliff slabs.

### G. Competitive intelligence from catalogs
- G1 Self-updating catalog watcher, platform, W0: versioned snapshots, diffs become dated events.
- G2 Dual-network natural experiment, E6, W0+W1.
- G3 Proposition gap index, E6, W0+W1.

### H. Trust and use
- H1 Provenance ribbon, W0. H2 Data-drift monitor, W1. H3 Forecast accountability, W1. H4 Analyst annotations (become candidate causes), W0. H5 Pitch pre-mortem, W2+W3. H6 Role-based briefs and tripwires, W1. H7 Findings to slide (NPCI template), W0. H8 Scenario cards, W0.

## Interactive modules (17)
M1 deal projection sliders (existing engine); M2 multi-card CVP comparator (headline versus realised value); M3 offer designer; M4 counterfactual toggle; M5 time machine slider; M6 threshold designer; M7 cap designer; M8 cohort builder; M9 funnel with levers (feeds M1); M10 wallet-flow dial; M11 rail-migration slider; M12 substitution explorer; M13 clickable waterfall; M14 "what would have to be true" solver; M15 tornado chart; M16 benefit dials; M17 reward-rationality view. Evidence-fed multipliers: M3 and M9 should replace hand-set Deal Model multipliers with measured effects.

## Open decisions
1. Engines in the browser (a tested JavaScript copy per engine) or a small local service; recommendation: service for many-lever modules, browser for the Deal Model.
2. Starting pair suggested: A1 and G1 (their data already exists).
3. Internal models to confirm: encrypted ID stability across card and UPI; BIN-to-variant mapping; how offers are tagged in Trino; whether interchange is stored per BIN or per rail.
