# W3: Proposition change impact

**Trigger:** Event: approval of a proposition event or a major offer; Scheduler follow-ups at D+30 and D+60

## Canvas (Workflow > New workflow; one node per line)
```
Start (event)
 -> Agent: Impact Analyst (define treated/control, record baseline via SQL)
 -> Scheduler: create follow-up tasks for D+30 and D+60
 -> At each follow-up: Impact Analyst measures DiD, writes PROPOSITION_IMPACT finding
 -> Critic -> Writer -> Curator Queue
```

## Produces
Measured effect of every CVP/MITC change and major offer; playbook proposals.

## Models and cost control
Opus for design, Sonnet for follow-ups.
