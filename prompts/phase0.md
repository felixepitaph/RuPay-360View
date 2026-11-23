# Phase 0 prompt: paste this into your internal Claude or ChatGPT session

You are working in the repository `rupay-360-platform`. Before doing anything, read:
- `AGENTS.md`
- `docs/PHASES.md`
- `docs/PHASE0_CHECKLIST.md`
- `docs/reference/03_trino_semantic_layer.md`

Confidential documents for this task are in `docs/internal-context/`.

Create a branch called `phase-0-skeleton`.

Your task is Phase 0 only:
1. Use `scripts/trino_probe.py` to explore Trino (catalogs, schemas, tables, describe). Never write
   anything to Trino. Do not print raw rows containing card numbers.
2. Find the tables for: card-rail transactions, UPI credit-card transactions, UPI merchant tier / MDR
   classification, and Cards-in-Force. Record exact names, columns, date columns and freshness in
   `docs/PHASE0_CHECKLIST.md` section A.
3. Answer the five discovery gaps in section C using what you actually find in Trino and in
   `docs/internal-context/`. If something cannot be determined, say so and list what you need from me.
4. Using the internal documents, list the BINs, product codes and card names for YES Bank and
   IDFC FIRST Bank in section D. Do not copy confidential rates anywhere that is committed.
5. Write one SQL file in `sql/` that returns monthly GMV, approved transactions and distinct active
   cards for one YES or IDFC RuPay BIN. Run it with `trino_probe.py query-file ... --out data/phase0_smoke.json`.
6. Build the smallest possible web page (plain HTML plus one chart library is fine) that loads
   `data/phase0_smoke.json` and draws a monthly GMV chart. Number formats: Indian style, rupees in crore.
7. Fill in `docs/METRIC_DICTIONARY.md` with your proposed definitions based on what the data supports.
   Mark each as "proposed" for me to confirm.
8. Record anything that differs from the reference docs in `docs/DECISIONS.md`.

Do not start the Proposition Hub, the deal engine or any later phase.
When finished, commit, open a pull request, and summarize: what you found, what is still unknown, and
what you need from me.

## Added 2026-11-23 (AiNxt re-run)
4. Fill the placeholders in `sql/agg_weekly_issuer_merchant.sql` and `sql/txn_weekly_card_merchant.sql`
   with the real table and column names you found; record each mapping in `docs/PHASE0_CHECKLIST.md`.
5. With `R360_SOURCE=trino`, run `PYTHONPATH=engine python -m r360 sql "SELECT COUNT(*) AS n FROM agg_weekly_issuer_merchant"`
   (or save the query output as snapshot files and use `R360_SOURCE=local:<folder>`).
6. Run `PYTHONPATH=engine python -m r360 watch` on the latest week and report the flags. Do not investigate yet.
