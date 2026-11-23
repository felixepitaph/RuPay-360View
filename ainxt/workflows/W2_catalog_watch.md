# W2: Catalog watch (CVP, MITC, offers)

**Trigger:** Scheduler: daily 06:10 IST; on demand when a PDF is dropped in the project folder

## Canvas (Workflow > New workflow; one node per line)
```
Start
 -> Web Agent: open each source in catalog/sources/registry.json (and the jobs in ainxt/web_agent_jobs/), scroll, copy page text
 -> Tool: r360_source_check (hash compare)  --unchanged--> skip
 -> Agent: Document Agent (extract changes; propose catalog change + proposition event)
 -> Tool: r360_validate_catalog on the proposed file
 -> Agent: Reconciler (conflicts vs MITC)
 -> Curator Queue: analyst approves / edits / rejects
 -> On approval: ADLC Pipeline (Governance or Feature) or Code agent merges into the repo; registry hash updated
 -> Trigger W3 for each new proposition event
```

## Produces
Up-to-date catalogs with sources; change log via merge history.

## Models and cost control
Extraction on Sonnet 5.5; bulk PDF text on a free local model (qwen-3.6) first, Sonnet only for the changed sections.
