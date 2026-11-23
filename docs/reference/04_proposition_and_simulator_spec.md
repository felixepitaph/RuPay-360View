# 03 — Proposition Control Plane JSON Schemas & Deterministic Simulator Spec

> **Core Principle:** LLMs extract unstructured CVP pages, MITC PDFs, and bank/network offer portals into these strict, versioned JSON schemas—and write natural-language explanations. **LLMs never compute final simulator numbers or financial yields.** All calculations run inside `packages/simulator-engine/` with deterministic unit tests.

---

## 1. Canonical Card & BIN Master (`schemas/dim_card_bin_master.schema.json`)

Binds Trino BINs, cross-network competitors (Visa/Mastercard), Deal Model variants, and Proposition catalogs into one spine.

```json
{
  "card_id": "HDFC_TATA_NEU_INF_RUPAY",
  "dual_network_pair_id": "HDFC_TATA_NEU_INF",
  "network": "RUPAY",
  "issuer_bank": "HDFC Bank",
  "card_name": "Tata Neu Infinity HDFC Bank Credit Card",
  "cardholder_profile": "Affluent",
  "variant_tier": "Select",
  "network_tier_ladder": "TIER_3_AFFLUENT",
  "collateral_type": "UNSECURED",
  "issuance_type": "CO_BRAND",
  "cobrand_focus": "DISCRETIONARY",
  "cobrand_partners": ["Tata Digital"],
  "is_virtual_floater": false,
  "parent_primary_network": null,
  "trino_keys": {
    "bin_match_rule": "8_DIGIT",
    "bins": ["65301510", "65301512"],
    "prodcodes": ["RUPAY_SEL_CC"],
    "deal_project_id": "DEAL_HDFC_FY27",
    "deal_variant_idx": 0
  },
  "is_in_trino": true
}
```

* **Cross-Network Tier Equivalence Ladder (`network_tier_ladder`):**
  * `TIER_1_MASS`: RuPay Classic/Platinum ↔ Visa Classic/Gold ↔ MC Standard/Titanium
  * `TIER_2_MASS_AFFLUENT`: RuPay Platinum/Select ↔ Visa Platinum ↔ MC Titanium/World
  * `TIER_3_AFFLUENT`: RuPay Select ↔ Visa Signature ↔ MC World
  * `TIER_4_SUPER_PREMIUM`: RuPay EKAA ↔ Visa Infinite ↔ MC World Elite

---

## 2. CVP Catalog (`schemas/cvp_catalog.schema.json`)

Separates **Network-Funded Perks** from **Issuer-Layered Rewards** and logs versioned change events that automatically generate Telemetry Overlay pins.

```json
{
  "card_id": "HDFC_TATA_NEU_INF_RUPAY",
  "version_id": "cvp_2026.2",
  "effective_from": "2026-07-01",
  "effective_to": null,
  "source_hash": "sha256:...",
  "change_event": {
    "type": "DEVALUATION",
    "summary": "Added ₹50,000 quarterly spend gate for domestic lounge access"
  },
  "fees": {
    "joining_fee_inr": 1499,
    "annual_fee_inr": 1499,
    "is_ltf": false,
    "waiver_annual_spend_inr": 300000,
    "waiver_excluded_mccs": ["6513", "6540", "5541"]
  },
  "reward_currency": {
    "name": "NeuCoin",
    "point_value_inr_base": 1.0,
    "point_value_inr_cash": 0.0,
    "point_value_inr_travel_partner": 1.0
  },
  "network_funded_layer": {
    "upi_cc_enabled": true,
    "network_lounge_dom_qtr": 2,
    "network_lounge_intl_yr": 2,
    "network_program_perks": ["RuPay Select Wellness", "Golf Access", "OTT Bundle"]
  },
  "earn_rules": [
    {
      "rule_id": "UPI_PARTNER_APP",
      "rails": ["UPI_CC"],
      "payment_modes": ["FS"],
      "eligible_tpap_apps": ["TATA_NEU_UPI"],
      "eligible_mccs": ["ALL_NON_EXCLUDED"],
      "min_txn_inr": 100,
      "earn_rate_pct": 1.5,
      "monthly_cap_inr": 500,
      "quarterly_spend_gate_inr": 0
    },
    {
      "rule_id": "UPI_OTHER_APPS",
      "rails": ["UPI_CC"],
      "payment_modes": ["FS"],
      "eligible_tpap_apps": ["OTHER_TPAP"],
      "eligible_mccs": ["ALL_NON_EXCLUDED"],
      "min_txn_inr": 100,
      "earn_rate_pct": 0.5,
      "monthly_cap_inr": 500,
      "quarterly_spend_gate_inr": 0
    },
    {
      "rule_id": "BASE_RETAIL",
      "rails": ["POS", "ECOM", "INTL"],
      "payment_modes": ["FS"],
      "eligible_mccs": ["ALL_NON_EXCLUDED"],
      "min_txn_inr": 0,
      "earn_rate_pct": 1.5,
      "monthly_cap_inr": null,
      "quarterly_spend_gate_inr": 0
    }
  ],
  "milestones": [
    {
      "period": "QUARTERLY",
      "spend_threshold_inr": 150000,
      "reward_value_inr": 1000,
      "excluded_mccs": ["6513", "6540", "4900"]
    }
  ],
  "lounge_and_lifestyle": {
    "dom_lounge_per_qtr": 2,
    "intl_lounge_per_yr": 4,
    "lounge_spend_gate_qtr_inr": 50000,
    "fuel_surcharge_waiver_pct": 1.0,
    "fuel_min_txn_inr": 400,
    "fuel_max_txn_inr": 5000,
    "fuel_monthly_cap_inr": 500
  }
}
```

---

## 3. MITC Policy & Friction Schema (`schemas/mitc_catalog.schema.json`)

Captures pricing, EMI rules, Secured FD terms, RBI Network Choice portability friction, and MCC exclusions/surcharges.

```json
{
  "card_id": "IDFC_WOW_RUPAY",
  "version_id": "mitc_2026.2",
  "effective_from": "2026-08-01",
  "source_hash": "sha256:...",
  "cost_of_credit": {
    "apr_pct": 35.0,
    "monthly_interest_pct": 2.92,
    "grace_period_days": 48,
    "cash_advance_fee_pct": 0.0,
    "cash_advance_min_inr": 199
  },
  "international_friction": {
    "forex_markup_pct": 0.0,
    "dcc_markup_pct": 1.0,
    "zero_forex_flag": true
  },
  "secured_fd_terms": {
    "is_secured_fd": true,
    "min_fd_inr": 10000,
    "credit_limit_to_fd_pct": 100,
    "auto_renewal_required": true
  },
  "network_portability": {
    "rbi_network_choice_offered": true,
    "available_networks": ["RUPAY", "VISA"],
    "network_change_reissue_fee_inr": 199
  },
  "emi_policy": {
    "processing_fee_flat_inr": 199,
    "processing_fee_pct": 0.0,
    "emi_apr_min_pct": 14.0,
    "emi_apr_max_pct": 16.0,
    "foreclosure_fee_pct": 3.0,
    "emi_earns_base_rewards": true,
    "emi_counts_toward_waiver": true,
    "emi_counts_toward_milestone": false
  },
  "reward_and_surcharge_rules": {
    "reward_excluded_mccs": ["5541", "5542", "6513", "6540"],
    "category_surcharges": [
      { "group": "RENT", "mccs": ["6513"], "fee_pct": 1.0, "free_monthly_limit_inr": 0 },
      { "group": "UTILITY", "mccs": ["4900"], "fee_pct": 1.0, "free_monthly_limit_inr": 20000 }
    ],
    "redemption_fee_inr": 99,
    "points_expiry_months": null
  },
  "penalties": {
    "late_fee_max_inr": 1250,
    "overlimit_fee_pct": 2.5,
    "overlimit_min_inr": 500
  }
}
```

---

## 4. Offers Catalog (`schemas/offers_catalog.schema.json`)

Explicitly separates **Full Swipe (`FS`)** from **`EMI`** offers and joins directly to `agg_daily_bin_merchant` via `merchant_id`.

```json
{
  "offer_id": "OFF_IDFC_ZEPTO_202611_EMI",
  "offer_source": "ISSUER",
  "network_scope": ["RUPAY", "VISA", "MASTERCARD"],
  "issuer_bank": "IDFC FIRST Bank",
  "eligible_card_ids": ["ALL_IDFC_CC"],
  "eligible_variant_tiers": ["Platinum", "Select", "EKAA"],
  "merchant_id": "MERCH_ZEPTO",
  "merchant_brand_normalized": "ZEPTO",
  "mcc": "5411",
  "category": "Quick Commerce",
  "rails": ["ECOM", "UPI_CC"],
  "payment_mode": "EMI",
  "emi_tenures_months": [3, 6, 9],
  "benefit": {
    "type": "INSTANT_DISCOUNT",
    "rate_pct": 10.0,
    "flat_inr": 0,
    "min_txn_inr": 3000,
    "max_cap_inr": 1000,
    "usage_limit": "1_PER_CARD_PER_MONTH"
  },
  "stackable_with_base_cvp": false,
  "validity": {
    "start_date": "2026-11-01",
    "end_date": "2026-11-30",
    "days_of_week": ["ALL"]
  },
  "funding_split_internal": {
    "network_pct": 0,
    "issuer_pct": 60,
    "cobrand_partner_pct": 0,
    "merchant_pct": 40
  }
}
```

---

## 5. Configurable Interchange Rule Interface (`schemas/interchange_rules.schema.json`)

> **Security & Confidentiality Rule:** Never hardcode real interchange schedules in UI code or external prompts. During initial builds, seed this isolated config with `[DUMMY PLACEHOLDER RULES]`. Internal deployment swaps the JSON/table source with actual confidential rates from `/docs/internal-context/`.

```json
{
  "rule_set_version": "DUMMY_V1_REPLACE_INTERNALLY",
  "is_placeholder": true,
  "rules": [
    {
      "rule_id": "UPI_SMALL_OFF_LTE_2K",
      "rail": "UPI_CC",
      "payment_mode": "FS",
      "upi_merchant_type": "SMALL",
      "upi_merchant_genre": "OFFLINE",
      "ticket_cliff": "LTE_2K",
      "mcc_bucket": "ALL",
      "interchange_bps_by_variant": { "Platinum": 0, "Select": 0, "EKAA": 0 },
      "network_fee_mode": "ACTUAL_TRINO_SWITCHFEE"
    },
    {
      "rule_id": "POS_ECOM_EMI",
      "rail": "POS_OR_ECOM",
      "payment_mode": "EMI",
      "upi_merchant_type": null,
      "upi_merchant_genre": null,
      "ticket_cliff": "GT_3K",
      "mcc_bucket": "CONSUMER_DURABLES_RETAIL",
      "interchange_bps_by_variant": { "Platinum": 120, "Select": 135, "EKAA": 150 },
      "network_fee_mode": "DEAL_RVP_PLUS_RFF"
    }
  ]
}
```

---

## 6. Deterministic Customer Spend & Reward Simulator Spec (`packages/simulator-engine/`)

### Inputs
* `selected_card_ids`: 2 to 4 cards (any mix of banks and RuPay/Visa/Mastercard).
* **8 Monthly Spend Buckets:** `upi_partner_tpap`, `upi_other_tpap` (plus `% txns < ₹100`), `online_fs`, `offline_pos`, `groceries_qcom`, `fuel_utilities_rent`, `travel_hotels`, `international`, and `emi_purchases` (with avg basket & tenure).
* **Toggles:** `include_active_offers` (boolean), `include_lifestyle_valuation` (boolean).

### Deterministic Equations (Annualized per Card)
1. **Effective Annual Fee:**
   $$\text{EffFee} = \begin{cases} 0 & \text{if } \text{EligibleAnnualSpend} \ge \text{waiver\_annual\_spend\_inr} \\ \text{annual\_fee\_inr} & \text{otherwise} \end{cases}$$
2. **MITC Friction Drag:**
   $$\text{Friction} = \text{EffFee} + (\text{IntlAnnual} \times \text{forex\_markup\_pct}) + \sum_{g} \max(0, \text{Spend}_g - \text{FreeLimit}_g) \times \text{FeePct}_g + \text{EmiProcFees} + \text{RedemptionFees}$$
3. **Net Customer Value & Yield:**
   $$\text{NetValue} = \text{BaseCvpEarn} + \text{MilestoneBonus} + \text{ActiveOfferBoost} + \text{LifestyleValue} - \text{Friction}$$
   $$\text{NetYield\%} = \frac{\text{NetValue}}{\text{TotalAnnualSpend}} \times 100$$

### Telemetry Reality Check (Mandatory Output Panel)
For every simulated RuPay card, join `TotalMonthlySpend` directly to `agg_monthly_user_slabs_churn` and `Card Economics`:
1. Identify the exact **User Spend Slab** (`Slab 1`–`Slab 6`) and display the **% of that card's actual Trino active base** sitting in that slab.
2. Compare **Simulated Customer Net Yield (%)** against the card's **Realized Blended Interchange Yield (%)**. If $\text{NetYield\%} > \text{InterchangeYield\%}$, flag the card as **Revolver / Partner-Subsidy Dependent** (elevated MITC devaluation risk).