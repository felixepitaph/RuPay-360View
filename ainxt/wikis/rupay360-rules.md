# Wiki: rupay360-rules (attach to every RuPay 360 harness)

1. **Numbers come from tools.** Get every figure from a SQL query (`r360_sql`) or an engine (`r360_deal_engine`, Watcher, evidence tests). You may design new metrics and write the SQL for them; you may not do the arithmetic yourself. Quote numbers exactly as returned (rounding for display is fine).
2. **Cite everything.** Each number: the tool call or SQL hash. Each proposition fact: document or URL, page or section, date retrieved.
3. **Read-only data.** Only SELECT queries. Column restrictions are set by the data team and internal models in `engine/config/restrictions.json`; obey whatever it says, and if a query is refused, aggregate or drop the column. Do not commit credentials.
4. **Propose, never write.** Changes to catalogs, metrics, thresholds or playbooks go through a proposal tool and the Curator Queue. Findings are written by the pipeline with status PROPOSED.
5. **Association is not proof.** Say "likely" or "consistent with" unless a control comparison supports the claim; always name what you could not check.
6. **Scope.** YES BANK and IDFC FIRST Bank cards across RuPay, Visa and Mastercard. Other issuers appear only as control groups or market context.
7. **Confidential terms.** Interchange schedules and deal terms stay in the internal context folder; never paste them into findings, wikis or commits.
8. **Fees follow the MITC.** When a page and the MITC disagree on a fee, the MITC wins; record the conflict.
9. **Be brief.** Analysts read on the go: lead with the answer, then evidence, then cautions.
10. **Improve the process.** If the data or internal documents show a better way to do any of this, propose the change (merge request or Curator Queue proposal) with your evidence, and tell AK. Rules 1, 3, 4 and 7 stay fixed.
