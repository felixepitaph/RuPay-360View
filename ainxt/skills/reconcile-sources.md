---
name: reconcile-sources
description: Find and resolve conflicts between card pages, MITC documents and offer terms.
---

# reconcile-sources

Find and resolve conflicts between card pages, MITC documents and offer terms.

## Steps
1. For each card, compare: joining/annual fee and waiver, forex markup, fuel waiver, reward exclusions, lounge gates, between the CVP entry and the issuer MITC.
2. Classify each difference: MITC_NEWER, PAGE_NEWER, SAME_DATE_CONFLICT, PAGE_INTERNAL_CONFLICT.
3. Rule: fees and charges follow the MITC; marketing benefits follow the latest dated page; same-date conflicts go to the analyst.
4. Output a table and propose corrections only where the rule decides.
