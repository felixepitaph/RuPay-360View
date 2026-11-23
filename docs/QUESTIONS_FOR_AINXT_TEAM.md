# Questions for the AiNxt team (send as one message)

1. **Builder access.** Agent Builder and Factory show "Missing or invalid Authorization header" for me. What role or token do I need to create harnesses, skills, tools, wikis and workflows?
2. **Trino token.** You said AiNxt needs a JWT or API token to query Trino. Can you (or the data team) issue a read-only service-account token for the RuPay credit-card schemas, and should it go in Profile > API Token Vault?
3. **Tools.** The public npci/ainxt-enterprise code registers tools from external MCP servers (stdio/SSE) as `<server>__<tool>`. Does Buddy 2.0.1 do the same, and can I (or an admin) add a stdio server running `python3 tools/mcp_server.py` with environment variables? The public HTTP tool path allows only HTTPS and blocks private addresses: is that true here too? Which Python and network access does the MCP host have (Trino reachable)?
4. **Code from workflows.** Can a Workflow node or Scheduler task run a command in a repo (e.g. `python -m r360 run-insights`) on the AiNxt server, or only through the Code agent on my laptop?
5. **Git.** Which Git host does the ADLC Pipeline use for new products? Can I register a product "rupay-360" with repo and base branch?
6. **Curator Queue.** Can a harness add items to the Curator Queue (findings, catalog proposals), and can approvals trigger a workflow?
7. **Data handling.** Are card-level aggregates (no PAN, salted card key used only inside queries) allowed through AiNxt tools? Any logging or retention rules for tool outputs?
8. **Budget.** The workspace shows $0 / $250. Is that monthly? Are local models (qwen, gemma, deepseek) free for workflows and scheduler tasks too?
9. **Web Agent.** Can the Web Agent run inside a scheduled workflow (unattended), and can it read PDFs opened in the browser?
10. **Skills and wiki objects.** The public repo defines a skill as an ordered tool list or workflow (`skill_registry.py`). `ainxt/skills_registry.json` follows that. Where do Harness, Wiki and Curator Queue live in Buddy 2.0.1 (these words do not appear in the public code), and is there an import format for them?
11. **Sensitive-column rules.** Our code no longer hard-codes column restrictions (`engine/config/restrictions.json`, empty by default). The public database MCP server masks PAN, account number, mobile, email, Aadhaar, IFSC, keys and tokens, and the platform has a PCI/PII gate on tool inputs and outputs. Which rules are mandatory in Buddy 2.0.1 and which Trino permissions will the service account have? Our tools will follow whatever you set.
