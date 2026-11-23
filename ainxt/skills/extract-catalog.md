---
name: extract-catalog
description: Extract CVP, MITC or offer terms from a bank page, offer portal or PDF into the catalog schemas, with sources, only when the source changed.
---

# extract-catalog

Extract CVP, MITC or offer terms from a bank page, offer portal or PDF into the catalog schemas, with sources, only when the source changed.

## Steps
1. Get the page text (Web Agent, or a PDF in the project folder). For YES pages scroll to the bottom first; sections load lazily.
2. Call `r360_source_check(url, page_text)`. If `changed` is false, stop.
3. Read the matching schema in `schemas/` and the current entry (`r360_card` or `r360_catalog_search`).
4. Extract only what changed, value by value, copying numbers exactly as printed. Keep "prior to <date>" and "effective <date>" values separately and record the effective date.
5. Record contradictions inside the page in `page_conflicts`. Never resolve them by guessing. MITC wins on fees.
6. Call `r360_propose_catalog_change` with the change, the reason and sources (URL or file, page or section, date retrieved, content_hash).
7. If the change alters rewards, fees, exclusions or caps, also propose a proposition event (`catalog/events/proposition_events.json`) with direction ENHANCEMENT / DEVALUATION / NEUTRAL.

## Source facts to respect (see source-facts wiki)
- yes.bank.in needs JavaScript; creditrewardz.yes.bank.in is login-only (skip).
- YES offer T&Cs are PDFs at yes.bank.in/pdf?name=<file>; some links are dead.
- firstrewards.in lists FS/EMI tag and expiry only; caps and eligibility come from the IDFC booklet.
