---
name: learn-from-verdicts
description: Improve the platform from analyst verdicts: thresholds, priors and playbooks.
---

# learn-from-verdicts

Improve the platform from analyst verdicts: thresholds, priors and playbooks.

## Steps
1. Read `r360_scorecard`. For each cause type with 5+ verdicts:
   - precision < 0.6: propose stricter tests or a lower prior for that type;
   - many analyst-reported true causes of a type the engine never proposes: propose adding that cause type.
2. Look at WRONG findings with no true cause recorded; ask the analyst in the weekly digest.
3. Review flags never investigated or always rejected; propose Watcher threshold changes in `engine/config/watcher.json` (bump `version`).
4. Write confirmed patterns (3+ CORRECT findings with the same cause type and category) as playbook entries.
All outputs are proposals for the Curator Queue.
