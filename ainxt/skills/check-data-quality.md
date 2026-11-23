---
name: check-data-quality
description: Check the snapshot data before insights run.
---

# check-data-quality

Check the snapshot data before insights run.

## Checks (all via `r360_sql`)
1. Freshness: max(week_start) equals the expected latest week.
2. Volume: rows and total spend for the latest week vs the median of the previous 8 weeks (WARN below 0.8x, BLOCK below 0.5x).
3. Coverage: every issuer and every merchant seen last week appears this week.
4. Nulls in merchant_id, category, issuer_bank.
5. Schema: columns match the previous run.
Return PASS / WARN / BLOCK and the numbers.
