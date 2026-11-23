# W1: Daily insight run

**Trigger:** Scheduler: daily 07:40 IST (after the T+1 snapshot lands)

## Canvas (Workflow > New workflow; one node per line)
```
Start (Scheduler trigger)
 -> Tool: refresh snapshots (runs the reviewed SQL in sql/ on Trino, saves agg tables) [Code agent / server job]
 -> Agent: Data Quality Sentinel  --BLOCK--> stop, email "data not ready"
 -> Tool: r360_run_insights (Watcher + candidate causes + evidence tests -> findings with status PROPOSED)
 -> For each new finding (loop):
      Agent: Investigator  (adds investigation note; may run extra SQL; may propose metrics)
      Agent: Critic        (PASS / PASS_WITH_CAUTIONS / REJECT)
      if not REJECT -> Agent: Writer (narrative)
 -> Tool: build Insight Briefing page (python -m r360 briefing)
 -> Curator Queue: findings await analyst verdict (Right / Partly / Wrong)
 -> Email: top 5 headlines with links
```

## Produces
Findings in ledger/, briefing page, email. Analyst verdicts feed W7.

## Models and cost control
Investigator on Opus only for HIGH/MEDIUM flags or flags over Rs10 L; others on Sonnet. Cap: 15 flags per run (largest first).
