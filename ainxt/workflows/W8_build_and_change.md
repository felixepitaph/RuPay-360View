# W8: Build and change the platform

**Trigger:** Jira ticket (e.g. NPCI-xxxx) -> ADLC Pipeline

## Canvas (Workflow > New workflow; one node per line)
```
Jira ticket (Feature / Bug Fix / Governance)
 -> ADLC Pipeline on the rupay-360 repo (product + base branch)
 -> Code agent implements, runs `pytest` and `scripts/validate_catalog.py`
 -> Needs Approval -> you approve the merge request
```

## Produces
Every code, schema or catalog change reviewed and tested.

## Models and cost control
Auto (Routing) in Code; Opus for engine changes.
