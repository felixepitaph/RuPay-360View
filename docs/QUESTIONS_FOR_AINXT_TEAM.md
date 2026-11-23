# Questions for the AiNxt team (send as one message)

1. **Builder access.** Agent Builder and Factory show "Missing or invalid Authorization header" for me. What role or token do I need to create harnesses, skills, tools, wikis and workflows?
2. **Trino token.** You said AiNxt needs a JWT or API token to query Trino. Can you (or the data team) issue a read-only service-account token for the RuPay credit-card schemas, and should it go in Profile > API Token Vault?
3. **Tools.** How are Factory Tools registered: HTTP endpoint with a JSON schema / OpenAPI, MCP server, or Python code? Can a tool call an internal host (our tool server) and pass a bearer token from the vault?
4. **Code from workflows.** Can a Workflow node or Scheduler task run a command in a repo (e.g. `python -m r360 run-insights`) on the AiNxt server, or only through the Code agent on my laptop?
5. **Git.** Which Git host does the ADLC Pipeline use for new products? Can I register a product "rupay-360" with repo and base branch?
6. **Curator Queue.** Can a harness add items to the Curator Queue (findings, catalog proposals), and can approvals trigger a workflow?
7. **Data handling.** Are card-level aggregates (no PAN, salted card key used only inside queries) allowed through AiNxt tools? Any logging or retention rules for tool outputs?
8. **Budget.** The workspace shows $0 / $250. Is that monthly? Are local models (qwen, gemma, deepseek) free for workflows and scheduler tasks too?
9. **Web Agent.** Can the Web Agent run inside a scheduled workflow (unattended), and can it read PDFs opened in the browser?
