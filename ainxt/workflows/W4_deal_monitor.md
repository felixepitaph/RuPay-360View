# W4: Deal monitor

**Trigger:** Scheduler: monthly, 3rd working day after actuals load

## Canvas (Workflow > New workflow; one node per line)
```
Start
 -> Tool: load deal actuals (SQL)
 -> Agent: Deal Monitor (deal engine on plan and actuals; cliffs; re-forecast)
 -> Writer -> Curator Queue (alert cards) -> Email
```

## Produces
Deal-to-date BPS, cliff alerts, re-forecast.

## Models and cost control
Sonnet.
