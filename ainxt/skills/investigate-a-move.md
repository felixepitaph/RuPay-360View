---
name: investigate-a-move
description: Investigate an unusual move in spend for a merchant, card, category or issuer and find the most likely cause, with evidence.
---

# investigate-a-move

Investigate an unusual move in spend for a merchant, card, category or issuer and find the most likely cause, with evidence.

## Steps
1. Read the finding with `r360_get_finding` (or run `r360_run_insights` first). Note the flag: who, what, which week, how big, and the Watcher context (issuer_wide, partial_week).
2. Read the candidate causes and their tests already in the bundle. Do not repeat tests already run.
3. List what else could explain the move, using the `playbooks` wiki and your judgement:
   - offers not in the catalogs (network offers from RuPay/Visa/Mastercard, other banks' offers, merchant's own sale);
   - CVP / MITC changes (`r360_proposition_events`, `r360_card`);
   - seasonality and calendar (festivals, salary week, month end, long weekends);
   - acceptance or technical problems (decline rates, error codes, one acquirer or app);
   - data issues (late files, BIN mapping, merchant name changes).
4. For each live hypothesis, write the SQL that would show it and run it with `r360_sql` (state the purpose). Useful cuts: by card variant, by network, by channel (POS / e-com / UPI CC), by payment mode (FS / EMI), by ticket slab, by day of week, decline/error codes, new vs existing cardholders.
5. If a new ratio or metric would settle the question, define it in SQL and run it. If it proves useful, call `r360_propose_metric`.
6. Conclude: most likely cause, what supports it, what weakens it, what you could not check. Use "likely" unless a control comparison supports it.

## Output (appended to the finding as the investigation note)
- Most likely cause (one line) and confidence (HIGH / MEDIUM / LOW) with the reason.
- Evidence table: claim | number | tool call or SQL hash.
- Hypotheses rejected and why.
- What would confirm it (data or a question for the issuer).

## Never
Compute numbers yourself; claim causation without a comparison group; ignore a column restriction the tool reports; cite a source you did not open.
