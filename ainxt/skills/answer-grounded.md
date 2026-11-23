---
name: answer-grounded
description: Answer an analyst's question using only tools, with every number traced.
---

# answer-grounded

Answer an analyst's question using only tools, with every number traced.

## Rules
- Decide which tool answers each part; prefer existing findings and metrics before writing new SQL.
- Show each number with its tool call or SQL hash; show the date range and filters used.
- If the data cannot answer it, say so and say what data would.
- If the analyst gives a verdict on a finding ("that was right / wrong because ..."), record it with `r360_record_verdict`.
