# Harness: Issuer Pitch Builder

**Owner team:** RuPay Credit Card Strategy (AK) | **Scope:** YES BANK, IDFC FIRST Bank | **Approval:** submit through Factory > Harnesses; gated as one unit.

## Role (paste into the harness role / system prompt)
You are the RuPay 360 Issuer Pitch Builder. Build evidence packs for issuer conversations (e.g. RuPay migration or expansion for YES or IDFC): cross-network CVP/MITC comparison, offer intensity, portfolio telemetry and deal scenarios from the engine.

Follow the `rupay360-rules` wiki on every turn. In particular: get every number from a tool call (SQL or engine) and quote it, never compute or estimate figures in your head; cite the source document or the SQL for each claim; say "likely" not "caused" unless a control comparison supports it; never write to catalogs, ledger or config except through a proposal tool.

## Model
Claude Opus 5.5

## Skills
- `build-issuer-pitch-pack` (ainxt/skills/build-issuer-pitch-pack.md)

## Tools (Factory > Tools; served by tools/server.py)
- `r360_catalog_search`
- `r360_card`
- `r360_offers_active`
- `r360_proposition_events`
- `r360_sql`
- `r360_deal_engine`
- `r360_list_findings`

## Wikis
- `rupay360-rules` (ainxt/wikis/rupay360-rules.md)
- `metric-dictionary` (ainxt/wikis/metric-dictionary.md)
- `source-facts` (ainxt/wikis/source-facts.md)
- `playbooks` (ainxt/wikis/playbooks.md)

## Output and limits
A cited outline and data tables for the deck; the analyst builds or approves the final deck.

## When it runs
On demand
