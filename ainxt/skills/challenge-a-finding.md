---
name: challenge-a-finding
description: Challenge a finding before it is published: look for other explanations, weak comparisons and data problems.
---

# challenge-a-finding

Challenge a finding before it is published: look for other explanations, weak comparisons and data problems.

## Checklist (answer each with evidence from tools)
1. Data: is the week complete (`partial_week`, row counts via `r360_sql`)? Did BIN or merchant mapping change?
2. Breadth: did the whole issuer, category or network move (`issuer_wide`, category totals)? Then the merchant story is probably wrong.
3. Comparison: is the control group sensible (same category, similar cards, same weeks)? Is it large enough?
4. Timing: does the move start when the cause starts and fade when it ends? Check the week before and after.
5. Size: is the claimed shift plausible for the offer size (e.g. Rs150 off cannot move a Rs50,000-ticket category)?
6. Alternatives: name at least two other explanations and whether data rules them out.
7. Sources: every catalog claim has a source; every number appears in the bundle or in your SQL.

## Verdict
- PASS: publish.
- PASS_WITH_CAUTIONS: publish with your cautions added.
- REJECT: do not publish; say what would change your mind.
