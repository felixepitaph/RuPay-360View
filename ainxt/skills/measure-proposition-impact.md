---
name: measure-proposition-impact
description: Measure what a CVP/MITC change or a major offer did to spend, activity and wallet share, with a control group.
---

# measure-proposition-impact

Measure what a CVP/MITC change or a major offer did to spend, activity and wallet share, with a control group.

## Steps
1. Identify the event (`r360_proposition_events` or offer), affected cards and categories, and the effective date.
2. Define treated cards (affected variants) and controls (same issuer unaffected variants, or other issuer's similar variants). Write down why the control is comparable.
3. Baseline: 8 weeks before. Measure windows: D+30 and D+60 (and offer window + 30 days after it ends for offers).
4. Run SQL for: spend, active cards, spend per active card, category share, wallet share where available, slab migration. Compute difference-in-differences in SQL.
5. Report the effect with a range (week-to-week spread of the control) and whether it persisted after D+30.
6. Propose a playbook entry if the effect is clear, e.g. "Rs150-off quick-commerce offers move ~X% of rival spend for one week, reverting within two weeks".
