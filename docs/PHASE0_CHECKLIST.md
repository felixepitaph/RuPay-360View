# Phase 0 checklist

Fill in as you go. Record what you actually find, not what the reference docs assumed.

## A. Connection
- [ ] `.env` filled in with a read-only Trino account
- [ ] `python scripts/trino_probe.py catalogs` works
- [ ] Catalogs/schemas holding card-rail, UPI CC, merchant tier and CIF data listed below

Tables found (path, one-line purpose, date column, row count if known):
-

## B. Questions for the data team (ask once, write the answers here)
1. Is the Trino account I use read-only? Can I create tables in any scratch schema?
2. Which tables hold card-rail transactions, UPI credit-card transactions, merchant tier / MDR classification?
3. Is there a Cards-in-Force (CIF) table, or a monthly issuer feed?
4. How fresh is each table (daily, T+1, monthly)?
5. Are there query limits (time, rows, concurrency) I should respect?
6. Is the card/user identifier hashed? Is there a key shared between card-rail and UPI data?

Answers:
-

## C. The 5 discovery gaps
| # | Gap | Finding (table.column) |
|---|---|---|
| 1 | CIF and issuance source | |
| 2 | Cross-rail user identity key (card-rail to UPI) | |
| 3 | How EMI is flagged | |
| 4 | International / cross-border flag | |
| 5 | Realized fee fields and interchange schedule source | |

## D. BINs for YES and IDFC FIRST
- [ ] List of BINs and product codes per card, with network and variant (from internal documents)
- [ ] Confirm 6-digit vs 8-digit matching per BIN

## E. First real number
- [ ] One agreed query (suggested: monthly GMV and active cards for one YES or IDFC RuPay BIN) saved to `data/`
- [ ] Compared with an existing Superset chart; difference explained

## F. Documents collected for Phase 1a
Per card: CVP page/PDF, MITC PDF, offer pages. Note file name and date.
-

## G. Added 2026-11-23
- [ ] Read-only Trino JWT issued; stored in AiNxt API Token Vault (and `.env` on the tool host)
- [ ] `sql/` templates filled; placeholder -> real column mapping written here
- [ ] Salted card key agreed with the data team (salt kept secret, never in the repo)
- [ ] `dim_merchant_master` keys added to `catalog/reference/merchant_master.json` (`trino_brand_keys`)
- [ ] First real Watcher run on the latest week; flags reviewed by hand
