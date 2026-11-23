# Review of all inputs against the vision (re-run, 2026-11-23)

Inputs reviewed: master blueprint and 3 spec docs, Gemini mockups V1 and V2, Deal Model V1.1 source,
YES MITC v18, IDFC MITC, IDFC Nov 2026 offers booklet, IDFC / YES card and offer web pages,
14 screenshots of the internal AiNxt platform.

## 1. Vision, restated in one line
Every move in spends, active rate, wallet share, economics and deal BPS should be explained by what
a card promises (CVP), restricts or charges (MITC) and temporarily subsidises (offers), and the
platform should find and explain those moves on its own, getting better as analysts correct it.

## 2. Gemini mockups (UI reference only, all data fake)
| Area | V1 | V2 | Verdict |
|---|---|---|---|
| Workspace structure (Telemetry / Proposition / Deal) | Flat 5 tabs | Matches blueprint (WS1/2/3, isolated filters) | Use V2 as the layout reference |
| Command Center KPIs, MCC, merchants, slabs | Yes | Yes | Keep |
| Card Economics | UPI-only ("UPI Economics & Slabs") | All rails | Use V2 |
| Wallet Share | UPI-only | Multi-rail | Use V2 |
| Proposition Hub (matrix, simulator, offers, overlay) | Partial | 4 sub-views, event pins, T=0 overlay, sparkline matrix | Use V2 |
| Deal Performance | Gauge in sidebar | 6 sub-tabs | Use V2 shape, engine from V1.1 |
| Banks shown | HDFC, SBI, Axis, IDFC, YES | Same | Restrict to YES and IDFC |
| **Insight / briefing feed** | None | None | **Missing. This is the core of the vision.** |
| **"Why did this move" panel with evidence and sources** | None | None | **Missing** |
| **Analyst feedback (right / wrong) on findings** | None | None | **Missing** (needed for learning) |
| **Catalog review queue, data freshness and provenance per number** | None | None | **Missing** |
| Copilot drawer | None | None | Missing (AiNxt chat can serve this) |
| Migration radar, near-cliff, acceptance leakage alerts | 1 static alert | None | Missing (now agent workflows) |

Conclusion: the mockups cover the *reporting* half. The *intelligence* half (find, explain, learn) is
absent from both and is what this re-run adds (see `docs/ARCHITECTURE.md`).

## 3. Deal Model V1.1
- The calculation core is about 70 lines (`calcV`, `calcAll`, attrition binary search). It is now
  ported to Python in `engine/r360/deal_engine.py` and checked against the blueprint reference numbers
  (`tests/test_deal_engine.py`). Agents call it as a tool; they never redo the maths.
- Issues found in V1.1 (kept as-is in the port so results match, logged for a later decision):
  1. Slab lookups run on the **portfolio total** of all variants (correct for one deal, note it).
  2. Milestone bonus uses only "year-end CIF ≥ 95% of target"; the blueprint also wants a
     `cif_spends` rule. Added as an option, default unchanged.
  3. The upfront payment is added to incentives in full (pro-rated view needed for Part B).
  4. The annual summary label hard-codes "25%" international revenue share (UI bug, not engine).
  5. Deal data lived in a cloud Supabase project. Keep deal terms on internal systems (D-005).

## 4. Documents and web sources (what we have, what is weak)
| Source | Status after re-run | Weakness |
|---|---|---|
| YES MITC v18 | Extracted | Network per variant still to confirm from BIN data |
| IDFC MITC | Extracted | No version number or effective date in the PDF |
| IDFC Nov 2026 booklet | Pages 3-5 earlier; **now all offer pages** (see catalog) | Many offers do not state eligible cards |
| IDFC card pages | 11 cards, LLM summaries | Re-extract from raw text via Web Agent |
| YES card pages | 11 cards, raw text | 19 co-brand pages left |
| YES offers page | 12 live credit offers, headlines | T&C PDFs need reading |
| firstrewards.in | Feasibility only | No caps or eligibility on the site |
| creditrewardz.yes.bank.in | Login only | Not usable |

## 5. AiNxt platform (from screenshots)
| AiNxt feature | Use in RuPay 360 |
|---|---|
| Chat with Claude Haiku/Sonnet/Opus 5.5, GPT-6.1, local models | Model choice per agent (cost control) |
| Projects (standing instructions, memory, document folder) | One project per workstream; memory = learned facts |
| Web Agent (Opus driving a browser) | Scraping bank pages and offer portals (replaces my manual browser work) |
| Agent Builder (drafts, approval) | Simple single agents |
| Workflow canvas (trigger -> agents, Deploy) | Multi-agent pipelines |
| Factory: Harnesses (role + skills + tools + wikis), Skills, Tools, Wikis, Activity, Curator Queue | The agent layer; Curator Queue = human approval |
| Scheduler (server-side, emails results) | Daily / weekly triggers |
| Code agent (local, Git clone with GitLab token) and ADLC Pipeline (Jira-driven, approval states) | Building and changing the repo |
| Governance, Marketplace | Approval of harnesses; reuse of shared agents |
| Budget shown: $0 / $250 workspace | Route bulk work to free local models |

Blocker seen in screenshots: Agent Builder and Factory show "Missing or invalid Authorization header".
Needs an API token / builder rights from the AiNxt team before anything can be deployed there.
