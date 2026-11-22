# 02 — Trino Semantic Layer, Canonical Spine & Discovery Template

> **Instructions for Internal AI Models (Phase 0):**
> Your environment has direct SQL access to the internal Trino data lake and access to `/docs/internal-context/`. **Do not rely solely on the observed fields below.** Run metadata discovery (`INFORMATION_SCHEMA.COLUMNS` / `SHOW TABLES`) first, update exact schema/table/column names in this file, resolve the 5 Discovery Gaps in Section 5, and log any upgrades in `docs/ARCHITECTURE_DECISIONS.md`.
>
> **Token Conservation Rule:** Raw UPI tables exceed 100+ columns. Keep this document curated to the **~25–30 whitelisted analytical columns per table** so monthly build prompts remain lean and accurate.

---

## 1. Observed Source Tables (Verify & Complete via Trino Metadata)

### 1.1 Card Rail Transactions (`<catalog>.rupay_txn.rupay_txns` — *verify exact path*)
* **Grain:** One row per card-rail authorization/transaction (POS, E-Com, International).
* **Observed Whitelisted Columns:**
  * Date / Time: `asdt` *(verify exact partition column)*
  * Card & Issuer: `pan` (masked/tokenized card key), `iss_bin`, `iss_bankname`, `iss_bnkcd`
  * Acquirer & Merchant: `acq_bankname`, `acq_bnkcd`, `mcc`, `mcc_desc`, `terminal_id`, `state`
  * Transaction & Status: `rrn`, `amt` (`DECIMAL`), `approve_decline_flag`, `reasoncodedesc`, `func_code_desc`, `transaction_type`
* **Verified Core Metric Expressions (from sample queries):**
  * Value (₹ Cr): `SUM(amt) / 10000000.0`
  * Volume (Mn): `COUNT(rrn) / 1000000.0`
  * ATS (₹): `SUM(amt) * 1.0 / NULLIF(COUNT(rrn), 0)`
  * Active Cards: `COUNT(DISTINCT pan)`
  * TPAC: `COUNT(rrn) * 1.0 / NULLIF(COUNT(DISTINCT pan), 0)`
  * SPAC: `SUM(amt) * 1.0 / NULLIF(COUNT(DISTINCT pan), 0)`

### 1.2 UPI RuPay Credit Card Transactions (`<catalog>.upi_txn.upi_rupay_cc_txns` & `upi_ft_txns` — *verify exact paths*)
* **Grain:** One row per UPI transaction (`pracctype = 'CREDIT'` for CC on UPI).
* **Observed Whitelisted Columns:**
  * Date & Cycle: `asdt`, `txndate`, `authdate`, `cycle`, `currency`
  * Routing & Banks: `payerbin`, `prodcode`, `purposecode`, `initmode`, `remitter_bank`, `beneficiary_bank`, `payer_psp_bank`, `payee_psp_bank`
  * Status & Friction: `approved_flag` (`'APPROVED'` → `'SUCCESS'`), `errcode`, `response_description`, `remrespcode`, `benrespcode`
  * Amount & Merchant: `txnamount`, `mcc`, `mcc_code_description`, `st.payeemerchant_mid`, `st.payeemerchant_tid`, `st.payeemerchantbrand`, `st.payeemerchantgenre`, `st.payeemerchantlegal`, `st.payeemerchantownership`, `st.cashback`, `st.invoice_date`, `st.payer_acct_type`
  * Realized Network Economics: `switchfee1`, `switchfee2`, `switchtaxamt1`, `switchtaxamt2`, `interchange` / `intfee*` / `switchfee*rebate` *(verify exact column spellings from `DESCRIBE`)*

### 1.3 UPI Merchant Tier / MDR Classification Table (*verify exact table name*)
* **Observed Whitelisted Columns:** `bin`, `prodcode`, `attribute`, `payeemerchant_mid`, `slab`, `small_offline_lte_2k`, `small_offline_gt_2k`, `large_offline`, `online`.
* **Business Purpose:** Separates zero-MDR small-offline micro-spends (`<= ₹2,000`) from monetizable spend (`> ₹2,000`, `large_offline`, `online`).

### 1.4 User-Level UPI Wallet Share (`user_spend` joined to `this_card_spend` — *verify if materialized table or CTE*)
* **Observed Output Metrics (per BIN):**
  * `this_card_spend`
  * `other_cards_spend = GREATEST(u.total_credit_spend - COALESCE(t.this_card_spend, 0), 0)`
  * `savings_spend`, `current_spend`
  * `total_upi_spend = this_card_spend + other_cards_spend + savings_spend + current_spend`
  * Percentage shares: `this_card_pct`, `other_cards_pct`, `savings_pct`, `current_pct`

---

## 2. Canonical Normalization Rules (Centralized — Never Inline in Tabs)

### 2.1 Centralized 6- vs. 8-Digit BIN Resolution (`dim_card_bin_master`)
Raw queries previously used ad-hoc `CASE WHEN SUBSTR(payerbin, 1, 8) = ... THEN SUBSTR(payerbin, 1, 6)`. **This pattern is prohibited inside dashboard tabs.**
* Maintain one authoritative mapping table `dim_card_bin_master` matching incoming `payerbin` / `iss_bin` by **longest-prefix match (8-digit BIN rule evaluated before 6-digit fallback)**.
* Joins `bin` + `prodcode` to: `card_id`, `dual_network_pair_id`, `issuer_bank`, `cardholder_profile`, `variant_tier`, `collateral_type` (`UNSECURED` | `SECURED_FD`), `issuance_type`, `cobrand_focus`, `is_virtual_floater`, `deal_project_id`, and `deal_variant_idx`.

### 2.2 Standardized Ticket-Size Slabs (`SLAB_D`)
Standardize this exact `CASE` expression in one reusable SQL macro/view across all modules:

```sql
CASE
  WHEN txnamount <= 100    THEN '0_100'
  WHEN txnamount <= 1000   THEN '100_1000'
  WHEN txnamount <= 2000   THEN '1000_2000'
  WHEN txnamount <= 5000   THEN '2000_5000'
  WHEN txnamount <= 10000  THEN '5000_10000'
  WHEN txnamount <= 25000  THEN '10000_25000'
  WHEN txnamount <= 50000  THEN '25000_50000'
  WHEN txnamount <= 99999  THEN '50000_99999'
  WHEN txnamount <= 100000 THEN '100000'
  WHEN txnamount <= 300000 THEN '100000_300000'
  WHEN txnamount <= 500000 THEN '300000_500000'
  WHEN txnamount > 500000  THEN '500000+'
  ELSE 'NULL'
END AS slab_d
```

### 2.3 Standardized Monthly User Spend Slabs (Distinct from `SLAB_D`)
Aggregated at `(month, unique_card_or_user_id)` total spend across rails:
`'<5K'`, `'5K_15K'`, `'15K_50K'`, `'50K_1L'`, `'1L_2.5L'`, `'2.5L+'`.
*Powers Command Center user segmentation, Near-Cliff waiver/milestone alerts, and the Proposition Spend Simulator Reality Check.*

---

## 3. Five Pre-Aggregated Materialized Views (UI Query Layer)

Frontend modules must query **only** these scheduled aggregation tables (never raw transaction scans):

| Materialized Table | Refresh | Grain | Primary Consumers |
| :--- | :--- | :--- | :--- |
| `agg_daily_bin_rail_mcc` | Daily (T+1) | `(dt, card_id, rail, payment_mode, upi_tier, mcc, slab_d, errcode)` | Command Center, Card Economics, Deal Actuals Auto-Feed |
| `agg_daily_bin_merchant` | Daily (T+1) | `(dt, card_id, merchant_id, rail, payment_mode)` | Top 20 Merchants, Daily Offer Lift & `D+30`/`D+60` Stickiness |
| `agg_monthly_user_slabs_churn` | Monthly | `(month, card_id, user_spend_slab, cohort_m0)` | CIF/Active Rate, User Spend Slabs, M0–M12 Churn Matrix, Near-Cliff Triggers |
| `agg_monthly_wallet_share` | Monthly | `(month, card_id, mcc, merchant_id)` | Multi-Rail Wallet Share, Silent Wallet-Migration Radar |
| `agg_geo_domestic_intl` | Monthly | `(month, card_id, geo_type, state_or_country, currency)` | Interactive India Map & World Map |

---

## 4. Analytical SQL Patterns to Implement

* **Rolling Momentum (`1M` vs. `3M`):** Compare `VALUE_1M` against `VALUE_3M / 3.0` per BIN, Rail, and `SLAB_D` to power executive momentum pills, Silent Wallet-Migration detection, and Deal Model 3-month trailing run-rate re-forecasting.
* **MID Acceptance Leakage:** Join `upi_rupay_cc_txns` against broader UPI P2M transactions on `st.payeemerchant_mid` for `txnamount > 2000`, flagging MIDs with high P2M bank-account success (`>95%`) alongside elevated RuPay CC decline rates (`>15%`).
* **Difference-in-Differences (DiD) Control Cohort:** For any `card_id` undergoing a CVP/MITC/Offer event on date $T_0$, compute daily indexed lift against peer RuPay cards sharing the same `(cardholder_profile, variant_tier, collateral_type)` with no event in $[T_0 - 30, T_0 + 30]$.

---

## 5. Phase 0 Discovery Checklist (Resolve Before Month 1 Build)

Internal AI models must inspect Trino + `/docs/internal-context/` and fill in the exact production answers below:

- [ ] **Gap 1 — CIF & Issuances Source:** Exact table/feed for total Cards-in-Force (CIF), monthly new issuances, and closures by BIN (`card_master` vs. RBI/issuer monthly upload).
- [ ] **Gap 2 — Cross-Rail User Identity Key:** Exact hashed customer/mobile identifier (if any) linking `pan` in `rupay_txns` to user wallets in `upi_txn` for full multi-rail individual Wallet Share.
- [ ] **Gap 3 — EMI Flagging:** Exact column/values identifying Checkout/POS EMI in `rupay_txns` (and whether Post-Purchase EMI data is available from issuer feeds).
- [ ] **Gap 4 — Cross-Border / International Indicator:** Exact column separating domestic vs. international transactions and merchant country in `rupay_txns` and `upi_txn`.
- [ ] **Gap 5 — Confidential Interchange & Switch Fee Mapping:** Exact `DESCRIBE` column names for realized switch/interchange/tax/rebate fields in `upi_txn`, plus internal rate schedules replacing dummy interchange placeholders.