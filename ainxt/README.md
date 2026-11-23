# Setting up RuPay 360 in AiNxt

Everything in this folder is written to be pasted into AiNxt screens. Order matters: tools before harnesses, harnesses before workflows, workflows before scheduler tasks.

## 0. Unblock access (ask the AiNxt team)
Your Agent Builder and Factory screens show **"Missing or invalid Authorization header"**. Ask for:
1. Builder rights for Agent Builder, Workflow and Factory in your workspace (or the role that grants them).
2. A **read-only Trino service account** issued as a JWT / API token (AiNxt said it needs one). Store it in **Profile > API Token Vault**, never in the repo.
3. How Factory **Tools** are registered. The public AiNxt Enterprise code (github.com/npci/ainxt-enterprise) registers tools from **external MCP servers** (stdio or SSE) as `<server>__<tool>`; `tools/mcp_server.py` is built for that. Confirm your Buddy 2.0.1 deployment does the same, and that an admin can add an external MCP server (the stdio command must be `python3`, `python`, `node`, `npx`, `uv`, `uvx` or `deno`). Fallbacks: `tools/server.py` (HTTP; the public code only allows HTTPS endpoints and blocks private addresses) and the CLI (`python -m r360 ...`).
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

## 3. Tools (register as an external MCP server)
**Preferred route.** In the admin area for external MCP servers add one server:
- Name: `rupay360` (the name becomes the tool prefix: `rupay360__r360_sql`, `rupay360__r360_run_insights`, ...)
- Transport: `stdio`
- Command: `python3`   Args: `["/path/to/repo/tools/mcp_server.py"]`
- Env: `R360_SOURCE=trino` plus the Trino variables from `.env.example`. Put the Trino token in the AiNxt Token Vault or the server's environment, never in the repo. Until Trino is connected use `R360_SOURCE=local:demo/data`.
The server must run on a machine that has Python 3.10+, `pip install -r requirements.txt` done, and network access to Trino.

**Check it worked** (run on that machine, no AiNxt needed): `python -m pytest tests/test_mcp_server.py`. In AiNxt: the 16 `rupay360__...` tools should be listed; call `rupay360__r360_deal_engine` with `{"scenario":"base"}` and expect net BPS 15.996.

**User-level rows and column restrictions.** Our code no longer hard-codes any personal-data column rule. `engine/config/restrictions.json` (empty by default) lists column-name patterns to refuse; the data team and your internal models own it, and the model may edit it on its own terms and report the change. `restrictions.example.json` has a starter list. Real enforcement should come from the Trino service account's permissions and AiNxt's own gates, so ask for an account that cannot read raw PAN, mobile, email or account columns. Per-user rows keyed by an encrypted ID work as soon as the data is available.

**Skills.** `ainxt/skills_registry.json` has one skill definition per markdown skill (name, description, ordered tools, tags), shaped like AiNxt's `SkillDefinition`. Regenerate with `python scripts/build_skill_registry.py --server-name <name you used>` if you named the server differently. The markdown skills stay the human-readable instructions.

**Caveat.** This follows the public npci/ainxt-enterprise code, which could not be run here against your Buddy 2.0.1. Names, fields and the admin screen may differ. If registration fails, send the error to the AiNxt team along with `docs/QUESTIONS_FOR_AINXT_TEAM.md`, or tell your internal model to adapt `tools/mcp_server.py` (it is allowed to, see AGENTS.md) and report the change.
HTTP fallback: run `tools/server.py` with `R360_TOOL_TOKEN` set and point each tool in `tools/tool_specs.json` at `POST /tools/<name>` with header `Authorization: Bearer <token>`.

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
