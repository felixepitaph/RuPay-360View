# Setting up RuPay 360 in AiNxt

Everything in this folder is written to be pasted into AiNxt screens. Order matters: tools before harnesses, harnesses before workflows, workflows before scheduler tasks.

## 0. Unblock access (ask the AiNxt team)
Your Agent Builder and Factory screens show **"Missing or invalid Authorization header"**. Ask for:
1. Builder rights for Agent Builder, Workflow and Factory in your workspace (or the role that grants them).
2. A **read-only Trino service account** issued as a JWT / API token (AiNxt said it needs one). Store it in **Profile > API Token Vault**, never in the repo.
3. How Factory **Tools** are registered: HTTP endpoint (OpenAPI / JSON schema), MCP server, or Python. `tools/tool_specs.json` and `tools/server.py` cover the HTTP case; the CLI (`python -m r360 ...`) covers the "run a command" case.
4. Whether workflows can call the Code agent or a server job (needed for the snapshot refresh and for writing findings).
5. Which Git host the Code agent and ADLC Pipeline use for this repo (the clone dialog uses a **GitLab** token).
Full list: `docs/QUESTIONS_FOR_AINXT_TEAM.md`.

## 1. Project
Projects > New project, name **RuPay 360**.
- Standing instructions: paste `wikis/rupay360-rules.md`.
- Memory: leave empty; AiNxt adds learned facts. Remove anything that is a number without a source.
- Document folder: the folder where you keep MITC PDFs, booklets and confidential sheets (stays on your laptop).

## 2. Repo
Code > Clone from Git (GitLab token) or Open folder on the unzipped repo. Run once: `pip install -r requirements.txt`, then `python -m pytest` (should pass) and `python demo/make_synthetic.py`.

## 3. Tools (Factory > Tools)
Register the 16 tools in `tools/tool_specs.json`. If Factory takes HTTP tools: run `tools/server.py` on the internal machine that can reach Trino, with `R360_TOOL_TOKEN` and the Trino token set, and point each tool at `POST /tools/<name>` with header `Authorization: Bearer <token>`.
Until Trino is connected, set `R360_SOURCE=local:demo/data` to use synthetic data.

## 4. Wikis (Factory > Wikis)
Create one wiki per file in `wikis/`: rupay360-rules, source-facts, glossary, playbooks, metric-dictionary.

## 5. Skills (Factory > Skills)
One skill per file in `skills/` (name and description are in each file's header).

## 6. Harnesses (Factory > Harnesses > New harness)
One per file in `harnesses/`: paste the Role, pick the model, attach the listed skills, tools and wikis, set owner team, submit for approval. Start with **01 Investigator, 02 Critic, 03 Writer, 11 Data Sentinel** (they make W1 work), then 04 Document Agent and 05 Reconciler (W2).

## 7. Workflows (Workflow > New workflow)
Build `workflows/W1_daily_insight_run.md` first, test it in the Preview pane on demo data ("Run the daily insight run for week 2027-01-04"), then Deploy. Then W2, W6, W7, W3, W4.

## 8. Scheduler
Paste the tasks in `scheduler/tasks.md`.

## 9. Curator Queue (your daily 10 minutes)
- **Findings:** mark Right / Partly right / Wrong, and type the true cause when Wrong. This is what makes the platform learn.
- **Catalog proposals:** check the source link, approve or edit.
- **Metric proposals:** approve only if the definition is clear and the SQL is right.
- **Threshold / playbook proposals:** approve when the scorecard supports them.

## Cost control (workspace budget $250)
- Free local models for bulk text (PDF to text, first-pass extraction, data checks).
- Haiku for writing, Sonnet for extraction and routine steps, Opus only for investigation, the Copilot and pitch packs.
- The Watcher and evidence tests are plain code (no model cost); agents only start on flagged moves, capped at 15 per run.
