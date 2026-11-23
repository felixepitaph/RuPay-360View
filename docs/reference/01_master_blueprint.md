# RuPay 360° — Network Portfolio Intelligence Platform
## Master Reference Architecture, Functional Specification & AI Build Methodology

> **Document Purpose & Audience**
> This document is the foundational blueprint and execution methodology for building the **RuPay 360° Network Portfolio Intelligence Platform** incrementally using internal high-tier AI models (**Claude** and **ChatGPT**). It consolidates all strategic intent, domain rules, data-lake observations, module specifications, and engineering governance defined during conceptualization.
>
> **Core Vision:** This is **not** a static BI dashboard or a consumer card-aggregator clone. The objective is to build an **interactive, intelligent, self-updating network operating platform** for the RuPay Credit Card team (Network / NPCI perspective) that unifies **Product, Portfolio, and Business** decision-making—and binds every quantitative metric directly to the qualitative **CVP, MITC, and Offers** that cause user and issuer behavior.

---

## 1. Mandate & Autonomy for Internal AI Models (Read First)

This blueprint was authored *without* access to confidential internal documents, raw production schemas, or live codebases. When this platform is built internally, the executing AI models will operate with **three major advantages** that fundamentally expand the lens beyond this document:

1. **Internal Confidential Context Repository:** The platform owner will upload a full repository of internal-only context documents (actual interchange & pricing circulars, internal product strategy decks, RBI/NPCI guidelines, exact Trino table DDLs, merchant classification dictionaries, and commercial deal policies).
2. **Direct Trino Data Lake Access:** The internal models can run live SQL and metadata queries (`INFORMATION_SCHEMA` / Hive Metastore) directly against the organization's Trino data lake to discover true schemas, table cardinalities, join keys, and real distributions.
3. **Direct GitHub Profile & Repository Access:** The internal models have direct access to the owner's GitHub repositories—including the original **Deal Model V1.1** codebase (`App.jsx`, `AppRouter.jsx`, `Auth.jsx`, `Projects.jsx`, `supabase-setup.sql`) and the new monorepo where this platform will live.

### Explicit Discretion & Evolution Clause
* **Treat this document as the Skeletal Architecture and Strategic North Star—not a rigid ceiling.**
* Whenever the uploaded internal context documents or live Trino data reveal richer fields, sharper business definitions, superior analytical cuts, or actual regulatory/interchange rules that improve upon assumptions in this document, **the internal AI models are explicitly authorized and expected to update, optimize, and elevate the architecture at their discretion.**
* **Governance Guardrail:** Whenever an internal model supersedes a placeholder rule, adds a newly discovered metric, or refines a schema from this document, it must:
  1. Log the change in `docs/ARCHITECTURE_DECISIONS.md` (what changed, which internal document or Trino table informed it, and why).
  2. Never silently alter verified mathematical formulas (especially the Deal Model engine) without updating unit tests and documenting the delta.
  3. Never expose credentials, keys, or raw confidential tables outside approved internal environments.

### How GitHub Access Supercharges the Monthly Token Budget
Having direct GitHub access solves the biggest failure mode of token-constrained AI development (re-pasting thousands of lines of code and schemas every month):
* **Zero-Waste Context:** Store all schemas, semantic docs, and internal context summaries in versioned files inside the repo (`/docs/context/`, `/schemas/`). Each monthly session reads only the specific files it needs rather than burning prompt tokens on boilerplate.
* **Exact V1.1 Parity:** Instead of reconstructing the Deal Model from prose alone, internal models can inspect the exact V1.1 `App.jsx` source directly in GitHub while porting it cleanly into a modular TypeScript engine.
* **Isolated Monthly Pull Requests:** Each monthly token allocation targets a single isolated package or tab on a feature branch, validated by automated unit tests before merging into `main`.

---

## 2. Core Product Thesis: Proposition-Bound Architecture

Most analytics tools treat marketing catalogs and transaction telemetry as two separate worlds. Consumer aggregators (such as Paisabazaar or BankBazaar) optimize for B2C lead generation and display static marketing promises; issuer portals (such as `firstrewards.in`) list active offers without portfolio economics.

**RuPay 360° operates on a single causal thesis:**
> **Every shift in Portfolio GMV, Active Rate, Wallet Share, Card Economics, and Commercial Deal Net BPS is downstream of what a card promises (CVP), what it restricts or charges (MITC), and what it subsidizes temporarily (Offers).**

Accordingly, the platform is structured into **four tightly bound architectural layers**:

| Layer | Role | Modules & Engines Powered |
| :--- | :--- | :--- |
| **Layer 1: Canonical Spine** | Unified dimension mapping (`dim_card_bin_master`, `dim_merchant_master`) resolving 6- vs. 8-digit BINs, `prodcode`, network tier equivalence, collateral type, and normalized merchant brands. | Universal join key binding every module and catalog together. |
| **Layer 2: Proposition Control Plane (The "Cause")** | Version-controlled, executable JSON rules for **CVP**, **MITC**, **Offers (FS vs. EMI)**, and **Configurable Interchange Schedules**. | Proposition Hub, Deterministic Customer Spend Simulator, Offer Lift Engine, Telemetry Event Pins. |
| **Layer 3: Telemetry & Economics (The "Effect")** | Scheduled, pre-aggregated Trino views covering macro portfolio velocity, all-rail unit economics, and multi-rail customer wallet share. | Command Center, Card Economics, Wallet Share. |
| **Layer 4: Commercial Agreements (The "P&L")** | Forward-looking issuer deal simulator (V1.1) and live Actual-vs-Baseline performance tracking (Part B) fed by Trino actuals and peer benchmarks. | Deal Performance (6 sub-tabs). |

---

## 3. Shell Architecture, Workspace Isolation & 3-Tier Filter Taxonomy

### 3.1 Collapsible Shell & Scoped Workspaces (Strict Rule)
* **Collapsible Left Navigation Rail:** Collapses cleanly from full navigation (`~220px`) down to an icon-only rail (`~56px`) so dense matrices, Deal Model tables, interactive maps, and multi-card comparisons can use 100% of the browser window.
* **Strict Global vs. Local Filter Separation:**
  * **Global Context Filter Bar applies ONLY to Workspace 1 (`Command Center`, `Card Economics`, `Wallet Share`).** Switching between these three tabs preserves the exact active bank, segment, rail, and payment-mode cohort.
  * **Workspace 2 (`Proposition Intelligence Hub`) does NOT inherit the Workspace 1 global bar.** It carries its own page-level filter bar—because users must filter across **multiple networks (`RuPay`, `Visa`, `Mastercard`)** and evaluate competitor cards absent from RuPay's Trino lake.
  * **Workspace 3 (`Deal Performance`) does NOT inherit the Workspace 1 global bar.** It is scoped by its own **Deal Project Switcher** (e.g., *Issuer B — FY27 Agreement*), **Perspective Role Toggle (`Network A` vs. `Issuer B`)**, and pinned **Net BPS Corridor Gauge**.

### 3.2 The 3-Tier Cascading Filter Taxonomy
To prevent users from getting confused about which filter restricts another—or accidentally locking themselves out of a universal view—filters are organized into **three visually distinct tiers** with explicit parent-to-child indentation, an **Active Scope Breadcrumb Strip**, and a one-click **`Reset to Universal View`** action:

| Filter Tier | Dimension | Selection Type | Cascading Sub-Filter & UX Rule |
| :--- | :--- | :--- | :--- |
| **Tier 1: Portfolio & Card Scope** | **Issuer Bank** | Multi-select | Allows comparing 1, several, or all banks simultaneously. |
| | **Cardholder Profile** | Multi-select | `Mass`, `Mass Affluent`, `Affluent`, `Super Premium`. |
| | **Variant Tier** | Multi-select | `Platinum`, `Select`, `EKAA` *(in Workspace 2, maps via Tier Equivalence Ladder to Visa/Mastercard tiers)*. |
| | **Collateral Type** | Toggle / Multi | `Unsecured` vs. `Secured (FD-Backed)`. |
| | **Issuance Type** | Toggle / Multi | `Proprietary` vs. `Co-Brand`. **Cascading Child Sub-Filter:** `↳ Co-Brand Focus` (`Discretionary` / `Non-Discretionary`) renders visibly indented under `Co-Brand` and stays disabled/dimmed unless `Co-Brand` is selected. |
| **Tier 2: Transaction Rail** | **Channel / Rail** | Multi-select | `Domestic POS`, `Domestic E-Com`, `UPI CC`, `International`. **Cascading Child Sub-Filter:** `↳ UPI Merchant Tier` (`Small Offline ≤₹2K`, `Small Offline >₹2K`, `Large Offline`, `Online`) enables indented underneath when `UPI CC` is active. |
| **Tier 3: Payment / Settlement Mode** | **Regular vs. EMI** | Segmented Toggle | `All` \| `Regular (Full Swipe / FS)` \| `EMI`. Treated cleanly as an orthogonal rail/mode so EMI spends, EMI-specific offers, and MITC EMI reward exclusions never bleed into full-swipe metrics. |

> **Active Scope Bar Example:**
> `Active Scope: HDFC Bank, IDFC FIRST • Affluent • Select • Unsecured • Co-Brand ↳ Discretionary • UPI CC ↳ Large Offline • EMI Only` + **`[↺ Reset to Universal View]`**

### 3.3 Visual & Financial UI Standards
* **Dual Theme Support via CSS Tokens:** Support **Dark Analytical Terminal** (extending Deal Model V1.1: `#070810` canvas, `#141826` cards, `#635bff` accent) and **Light Editorial Fintech** (Stripe/Mercury clarity for reading MITCs and screenshotting into leadership decks) via a single toggle.
* **Typography & Numerals:** `Inter` for UI, `JetBrains Mono` with `font-variant-numeric: tabular-nums` on every numeric KPI, cell, and axis.
* **Semantic Color Discipline:** Reserve Green, Amber, and Red strictly for **state/variance/corridor status**—never for decorative category palettes.
* **Auditability (`?` Breakdown Pattern):** Retain Deal Model V1.1's expandable **`?` Calculation Breakdown** on every KPI card across all modules so any stakeholder can inspect the exact Trino formula or engine derivation behind a number.
* **Shared Indian Formatters:** Centralize `f0` (Cr/L/K), `fR` (₹ Cr/L), `fP` (%), `fB` (bps), and `fVol` (Cr/Mn/L/K) in one shared utility package.

---

## 4. Trino Data Lake Landscape & Semantic Layer Architecture

### 4.1 Observed Trino Tables & Signals
Based on initial schema dumps and sample queries, the Trino environment spans these core datasets (to be fully verified and expanded by internal models via live metadata discovery):
* **Card Rail (`rupay_txns` / equivalent):** `pan`, `amt`, `rrn`, `mcc`, `mcc_desc`, `state`, `approve_decline_flag`, `iss_bankname`, `iss_bin`, `acq_bankname`, `transaction_type`, `func_code_desc`. Supports Crores/Millions rollups, `ATS`, `COUNT(DISTINCT pan)` active users, `TPAC`, and `SPAC`.
* **UPI CC Core & Realized Economics (`upi_txn` / `upi_rupay_cc_txns`):** `prodcode`, `purposecode`, `currency`, `cycle`, `remitter_bank`, `beneficiary_bank`, `payer_psp_bank`, `payee_psp_bank`, `approval_flag`, `errcode`, `mcc_code_description`, `txnamount`, realized network fees (`switchfee1`, `switchfee2`, `switchtaxamt1`, `switchtaxamt2`, interchange & rebate fields).
* **UPI Enriched Merchant Payload (`st.*`):** `st.payeemerchant_mid`, `st.payeemerchant_tid`, `st.payeemerchantbrand`, `st.payeemerchantgenre`, `st.payeemerchantlegal`, `st.payeemerchantownership`, `st.cashback`, `st.invoice_date`, `st.payer_acct_type`. Enables **brand-level** telemetry (e.g., Zepto, Swiggy, Croma, DMart) rather than just coarse MCC groupings.
* **UPI Merchant Tier / MDR Table:** `bin`, `prodcode`, `attribute`, `payeemerchant_mid`, `slab`, `small_offline_lte_2k`, `small_offline_gt_2k`, `large_offline`, `online`.
* **User-Level Wallet Share (`user_spend` joined to `this_card_spend`):** Computes `this_card_spend`, `other_cards_spend`, `savings_spend`, `current_spend`, `total_upi_spend`, and their percentage shares (`this_card_pct`, `other_cards_pct`, `savings_pct`, `current_pct`).
* **Standardized Ticket-Size Slabs & Velocity (`SLAB_D`):** 12 standardized transaction buckets (`0_100`, `100_1000`, `1000_2000`, `2000_5000`, `5000_10000`, `10000_25000`, `25000_50000`, `50000_99999`, `100000`, `100000_300000`, `300000_500000`, `500000+`) paired with rolling `VOL_1M` / `VALUE_1M` and `VOL_3M` / `VALUE_3M`.

### 4.2 Mandatory Canonical Spine Tables (Build First)
1. **`dim_card_bin_master`:** Centralizes conditional 6-digit vs. 8-digit `payerbin` normalization (`SUBSTR(payerbin, 1, 8)` vs. `SUBSTR(payerbin, 1, 6)`). **Never scatter `CASE WHEN SUBSTR(payerbin...)` across individual tab queries.** Key fields:
   * `card_id`, `dual_network_pair_id` (links identical bank cards issued on RuPay vs. Visa/MC), `network`, `issuer_bank`, `card_name`
   * `cardholder_profile`, `variant_tier`, `network_tier_ladder`
   * `collateral_type` (`UNSECURED` | `SECURED_FD`), `issuance_type` (`PROPRIETARY` | `CO_BRAND`), `cobrand_focus` (`DISCRETIONARY` | `NON_DISCRETIONARY`), `cobrand_partners[]`
   * `is_virtual_floater` (boolean), `parent_primary_network` (prevents misreading UPI-only virtual floaters as low-engagement standalone cards)
   * `trino_bin_match_rule` (`6_DIGIT` | `8_DIGIT`), `bins[]`, `prodcodes[]`, `deal_project_id`, `deal_variant_idx`
2. **`dim_merchant_master`:** Normalizes `st.payeemerchantbrand` and card-rail merchant strings into a canonical `merchant_id` tagged with `mcc`, `category`, and `default_merchant_type` (`SMALL` | `LARGE`).

### 4.3 Pre-Aggregated Materialized Layer (Performance Rule)
Never query raw transaction tables directly from UI components. Schedule **5 pre-aggregated Trino summary tables**:
1. `agg_daily_bin_rail_mcc` — Daily GMV, Txns, Approvals, Failure codes (`errcode`), FS vs. EMI, `SLAB_D`, UPI 2×2 merchant tiers, realized `switchfee*`.
2. `agg_daily_bin_merchant` — Daily brand-level GMV, Txns, Unique Cards, ATS split by FS vs. EMI (powers real-time daily Offer-to-Merchant lift tracking).
3. `agg_monthly_user_slabs_churn` — Monthly unique user spend-slab distributions, M0–M12 retention/churn cohorts, 30/60/90D active rates, and CIF joins.
4. `agg_monthly_wallet_share` — Multi-rail user wallet share (`this_card` vs. `other_cards` vs. `savings/current`) rollable by BIN, MCC, and Top 20 Merchants.
5. `agg_geo_domestic_intl` — State-level domestic rollups and country/currency-level international rollups.

### 4.4 Schema Discovery Checklist for Internal AI Models (Month 0 / Phase 1)
Before writing production SQL, the internal AI must query Trino metadata and internal docs to resolve five specific gaps:
1. **CIF & Issuances Source:** Identify the exact card-master / issuance / BIN-level CIF table (or monthly issuer reporting feed) to pair with active card counts (`COUNT(DISTINCT pan)`).
2. **Cross-Rail User Identity Key:** Confirm whether a shared hashed customer/mobile key links `pan` on POS/E-Com to UPI accounts in `upi_txn` (unlocking true cross-rail individual Wallet Share across different banks' cards).
3. **EMI Identification:** Verify how Checkout/POS EMI is flagged in Trino (`transaction_type` / terminal / BIN flags) vs. Post-Purchase EMI converted on issuer ledgers.
4. **International Transaction Flag:** Identify the exact cross-border / merchant-country / currency indicators on both card rails and UPI.
5. **Confidential Interchange Schedules:** Replace the dummy placeholder interchange table with the actual internal interchange & MDR rate matrices from the confidential repository.

---

## 5. Module-by-Module Functional Specifications

### 5.1 Command Center (Workspace 1 — Global Context Applied)
* **Core KPI Strip (All with `?` Formula Breakdowns & 1M-vs-3M Momentum):**
  `CIF`, `Active Cards (30D/60D/90D + Active Rate %)`, `GMV`, `Transaction Volume`, `ATS`, `Transactions per Active Card (TPAC)`, `Spend per Active Card (SPAC)`, and `Authorization Success Rate (ASR)`.
* **Required Granular Analytical Cuts:**
  1. **MCC-Level Spends + MITC Policy Overlay:** Ranked MCC spend view with automatic badges showing how many active issuers exclude or surcharge each MCC in their MITC.
  2. **App-Level Spends:** UPI TPAP breakdown (`payer_psp_bank` — PhonePe, GPay, Paytm, BHIM, Tata Neu, CRED, Kiwi, SuperMoney) + tokenized E-Com wallet/gateway share, surfacing co-brand app leakage.
  3. **Top 20 Merchants + Offer Correlation:** Joined via `dim_merchant_master`, displaying GMV, Txns, Unique Cards, MoM Δ%, and an inline **Active Offer Tag** (`RuPay Offer`, `Issuer FS/EMI Offer`, `Competitor Visa/MC Offer`) with lift vs. 28-day baseline.
  4. **Interactive Geography:** Toggle between an **Interactive India Choropleth Map** (domestic spends, active cards, ATS by `state`) and an **Interactive World Map** (international rail corridors overlaid with average MITC Forex Markup).
  5. **Monthly User Churn & Retention Cohort Matrix:** M0 → M12 triangle heatmap separating Unsecured vs. Secured (FD-backed) cohort retention, dormancy, and resurrection.
  6. **Spend-Based User Slabs & Near-Cliff Triggers:** Distribution of unique active users by monthly total spend (e.g., `<₹5K`, `₹5K–₹15K`, `₹15K–₹50K`, `₹50K–₹1L`, `₹1L–₹2.5L`, `>₹2.5L`). Directly cross-references CVP thresholds to count users sitting **10–15% below a quarterly milestone or annual fee-waiver gate** (actionable campaign targets).

### 5.2 Card Economics (Workspace 1 — Global Context Applied)
Replaces a UPI-only view with **full-network unit economics across all rails** (`Domestic POS`, `Domestic E-Com`, `UPI CC`, `International`, `EMI`):
* **Configurable Interchange Engine (`dim_interchange_rules`):** Never hardcode confidential rates into UI/SQL logic. Read from an isolated rule table resolved on:
  * **Card Rails (`POS` / `ECOM` / `INTL` / `EMI`):** `(Rail × Payment Mode × MCC Group × Card Variant [Platinum / Select / EKAA])`.
  * **UPI CC 2×2 Merchant Matrix:** `(Merchant Type [Small / Large] × Merchant Genre [Offline / Online] × Ticket Cliff [≤₹2K / >₹2K] × MCC Group × Card Variant)`, reconciled directly against realized `switchfee1/2` and taxes.
  * *Development Note:* Seed with clearly labelled `[DUMMY PLACEHOLDER RULES]` during scaffolding; swap with actual internal schedules once the confidential repository is ingested.
* **Ticket-Size Cliff & Failure Diagnostics (`SLAB_D` × `errcode`):** Visualize volume/value across all 12 `SLAB_D` buckets with failure-rate overlays highlighting the **₹2,000 small-offline MDR cliff** and the **₹1L / ₹5L NPCI UPI category caps**.
* **MID-Level Merchant Acceptance Leakage & MDR Spread Diagnostics:** Join `upi_rupay_cc_txns` against broader UPI P2M acceptance on `payeemerchant_mid` to identify active merchants accepting bank-account UPI > ₹2,000 while systematically declining/blocking RuPay CC > ₹2,000—creating an actionable acquirer intervention list.
* **EMI vs. Full-Swipe Economics:** Isolate EMI GMV share, ATS lift, and distinct interchange/subvention economics.

### 5.3 Wallet Share (Workspace 1 — Global Context Applied)
Expands beyond UPI-only share into **Multi-Rail Individual Customer Wallet Share**:
* **Full Spend Decomposition for Any Selected Cohort:**
  * `This Card` (split across POS, E-Com, UPI, EMI, Intl)
  * `Other Credit Cards` held by the same user (split across POS, E-Com, UPI)
  * `Savings / Current Account UPI` (`savings_spend` + `current_spend`)
* **Granular Drill-Downs:** Slice Wallet Share by **Card/Bank**, **MCC**, and **Top 20 Merchants**, directly correlated with **Active Offers, CVP updates, and MITC exclusions** to distinguish:
  * **Net-New Credit Creation** (`this_card_pct` rises while `savings_pct` / `current_pct` drops).
  * **Cross-Issuer Cannibalization** (`this_card_pct` rises while `other_cards_pct` drops—zero net network expansion).
* **Silent Wallet-Migration Radar:** Automatically flags cohorts where `VALUE_1M` fell >35% vs. `VALUE_3M / 3` *while* those users' total spend across other cards + savings accounts stayed flat or grew—isolating true top-of-wallet loss before dormancy hits.

### 5.4 Proposition Intelligence Hub — The Binding Control Plane (Workspace 2 — Independent Local Filters)
Carries its own complete local filter bar (including **Network: `RuPay` / `Visa` / `Mastercard`**, Banks, Segment, Variant Tier, Collateral `Secured/FD` vs. `Unsecured`, Issuance `Proprietary` / `Co-Brand ↳ Focus`, and `FS` vs. `EMI`) organized into **four integrated sub-views**:

#### A. Cross-Network Normalized CVP & MITC Comparison Matrix
* **Tier Equivalence Ladder:** Maps `RuPay Platinum / Select / EKAA` cleanly against Visa (`Classic–Platinum / Signature / Infinite`) and Mastercard (`Standard–Titanium / World / World Elite`).
* **Two-Layer Breakdown:** Explicitly separates the **Network-Funded Layer** (UPI CC access, RuPay Select/EKAA perks vs. Visa/MC network perks) from the **Issuer-Layered CVP & MITC**, flagging **Dual-Network Pairs** (identical bank cards issued on two networks).
* **MITC Friction & Policy Strip:** Side-by-side APR, grace period, Forex markup, EMI processing fee, `emi_earns_base_rewards`, `emi_counts_toward_milestone`, **Secured FD Lien Ratio & Min FD**, **RBI Network Choice & Portability Reissue Fee**, and **Excluded/Surcharged MCCs**, with a **`Show Differences Only`** toggle and versioned **MITC Devaluation Changelog**.

#### B. Deterministic Customer Spend & Reward Simulator
A pure-math TypeScript engine (LLMs extract the JSON schemas; they **never** calculate simulator outputs):
* Select 2–4 variants (any mix of banks or networks) and adjust monthly spend sliders across 8 buckets (`UPI Partner TPAP vs. Other TPAP` + `% txns < ₹100`, `Online Shopping FS`, `Offline POS Dining/Retail`, `Groceries & Quick-Com`, `Fuel/Utilities/Rent`, `Travel/Hotels`, `International`, `EMI Purchases`), plus an optional **Active Offers Toggle**.
* **Deterministic Formula (Annualized per Card):**
  $$\text{MITC Friction} = \text{Effective Annual Fee} + (\text{Intl Spend} \times \text{Forex\%}) + \sum (\text{Surchargeable Spend} \times \text{Surcharge\%}) + \text{EMI Processing Fees} + \text{Redemption Fees}$$
  $$\text{Net Customer Value (₹)} = \text{Base CVP Earn} + \text{Milestones} + \text{Active Offer Boost} + \text{Optional Lifestyle Valuation} - \text{MITC Friction}$$
  $$\text{Net Customer Yield (\%)} = \frac{\text{Net Customer Value (₹)}}{\text{Total Annual Spend (₹)}} \times 100$$
* **Telemetry Reality Check & Sustainability Link:** Maps the user's simulated monthly total directly into the Command Center **User Spend Slab** (showing what % of actual Trino cardholders sit in that slab) and compares **Simulated Net Customer Yield (%)** against **Realized Interchange Yield (%)** from Card Economics—flagging whether the card is interchange-funded or revolver/subsidy-dependent (high devaluation risk).

#### C. Synergized Offers Hub (`FS` vs. `EMI`) & Daily Merchant Lift Tracker
* Structured machine-joinable offer schema separating `offer_source` (`RUPAY_NETWORK`, `VISA_NETWORK`, `MC_NETWORK`, `ISSUER`, `COBRAND_PARTNER`), `merchant_id`, `payment_mode` (`FS` vs. `EMI`), `min_txn`, `max_cap`, `stackable_with_base_cvp`, `funding_split`, and `start_date`/`end_date`.
* **Synergized Analysis (`CVP + Offer + MITC`):** Computes true net customer value on a specific merchant basket (e.g., *Base CVP + 10% EMI Instant Discount − MITC EMI Processing Fee*).
* **Daily Real-Time Merchant Telemetry Link:** Joins active offers to `agg_daily_bin_merchant` to plot daily GMV, Txns, ATS, and Wallet Share before, during, and `D+30`/`D+60` after an offer window to separate sticky habit creation from one-off subsidy spikes.

#### D. 3-Mode Adaptive Telemetry Overlay + Causal Attribution (Solves 16-Variant Clutter)
Automatically adapts visualization based on cohort size, backed by **Difference-in-Differences (DiD)** causal attribution against a matched synthetic control cohort (same segment/variant without the event):
1. **Mode 1 — Direct Multi-Line + Clickable Event Pins (`1–4 Variants`):** Standard daily/monthly trend chart with annotated CVP, Offer, and MITC event pins.
2. **Mode 2 — Sparkline Anomaly Matrix (`5–16+ Variants`, Default):** Compact leaderboard table—one row per variant with a synchronized sparkline + inline event tick, flanked by `Pre-30D Avg`, `Post-30D Avg`, `DiD Net Lift %`, `Wallet Share Δ`, and `Slab Migration`. Checking 2–4 rows promotes them to Mode 1.
3. **Mode 3 — `T = 0` Event-Aligned Normalization (Cross-Date Cohorts):** Aligns disparate launch/devaluation dates onto a single relative axis (`T−30` to `T+30`, indexed to `100` at `T = 0`), plotting the **Cohort Median + P25–P75 Band** alongside outliers to quantify portfolio-wide sensitivity to specific policy changes (e.g., adding a ₹50K quarterly lounge gate).

### 5.5 Deal Performance (Workspace 3 — Independent Project Switcher, Full V1.1 + Part B Parity)
Must be ported **without shortcuts** into a pure, UI-free mathematical engine (`packages/deal-engine`) verified against the exact Section 11 reference benchmarks before UI integration, organized into **6 full sub-tabs**:

| Sub-Tab | Mode | Required Capabilities (Strict Spec Parity) |
| :--- | :--- | :--- |
| **1. Overview** | Plan (V1.1) | 6 KPI `InfoCards` with `?` breakdowns, Quarterly P&L combo chart, Revenue-to-Net Waterfall, Annual Summary table (dynamic `intlRevShare` label—fix hard-coded 25% bug), CIF Growth area, Monthly Spends (CC + UPI) stacked area. |
| **2. Projections** | Plan (V1.1) | Variant/Portfolio & Yearly/Monthly toggles, 3–7Y horizon, 50-iteration binary-search derived monthly attrition, per-year slider cards, Edit Table modal with live BPS badge, sticky Monthly Phasing table, draggable 12-bar Fiscal Seasonality Editor (Flat/Festive/Q4 Push/Ramp), plus **"Seed from Trino Peer Cohort"** benchmarking button. |
| **3. Revenue** | Plan (V1.1) | 5 KPI `InfoCards`, Annual Revenue & Incentive stacked bar charts, Year-End Volume & CIF Cliff Slab Proximity cards. |
| **4. Scenarios** | Plan (V1.1) | 5 Performance Multiplier sliders (30–200%), 2D Sensitivity Matrix heatmap (custom driver axes & min/max), Base / Conservative / Aggressive comparison table & chart. |
| **5. Configure** | Plan (V1.1) | Fee structure (`rvp`, `rff`, `ifp`, `intlRevShare`), per-variant quarterly `cardFee`, Volume & CIF cliff slab editors (add/remove), BPS floor/ceiling corridor, upfront impact panel, selectable **Milestone Rule (`cif` only vs. `cif_spends` ≥ 95%)**, **Issuer Break-Even Overlay** (comparing simulated CVP yield vs. realized interchange), strict read-only gating for `Issuer B`. |
| **6. Performance** | Live (Part B) | Immutable Locked Baseline snapshot (`deal_baselines` versioned table), Trino auto-fed + manual/XLSX Actuals grid (`deal_actuals` audit table) with 0–15% implied attrition validation, Re-forecast mode selector (`Hold Plan` / `3M Run-Rate` / `Manual` / optional AI Quant Engine), **Dual Deal-to-Date BPS (both pro-rated & full upfront shown side-by-side)**, Plan-vs-Actual-vs-Outlook charts, Sequential Substitution Revenue & Incentive Bridge (plus Economics Mix Variance from UPI ≤₹2K shift), Live Slab & Milestone Trackers, Remaining-Term Sensitivity Matrix + Binary-Search Floor/Target Solver, and SheetJS Excel Exports (with dynamic Formula Reference sheet). |

* **Mandatory Deal Engine CI Verification Suite (Default 1-Variant 5-Year Reference State):**
  * Derived Monthly Attrition (Y1–Y5): `0.000%`, `3.805%`, `4.607%`, `4.961%`, `5.161%`
  * Closing CIF (Y1–Y5): `60,000`; `120,000`; `180,000`; `240,000`; `300,000`
  * Total Spends: `₹16,596.0 Cr` | Gross Revenue: `₹65.672 Cr (39.57 bps)` | Total Incentives incl. Upfront: `₹39.125 Cr (23.57 bps)` | Net Revenue: `₹26.547 Cr`
  * **Net BPS:** `15.996` (Base) | `24.05` (Conservative) | `13.47` (Aggressive)
* **AI Signal Engine Role (Section 9 Compliance):** High-tier LLMs extract and classify qualitative market/relationship signals into the fixed JSON schema (`source weights`, `decay lambda`, `±25% cap`, `dedup cosine ≥ 0.85`, quarterly meta-learning with MAPE rollback) and write natural-language explanations—**they never generate raw projection numbers directly.**

---

## 6. Beyond a Dashboard: Interactive, Intelligent & Self-Updating Architecture

To fulfill the vision of a **living, intelligent platform** rather than a passive reporting tool, engineer four autonomous/interactive intelligence loops into the backend:

### 6.1 Automated Self-Updating Data & Catalog Pipelines
1. **Scheduled Trino Orchestration:** Daily (`T+1`) refresh of `agg_daily_*` and monthly refresh of `agg_monthly_*`, automatically updating the top-bar **Data Freshness Badge** and appending new actual months directly into live Deal Performance baselines (flagging partial month-to-date periods as provisional).
2. **Hash-Diff Qualitative Ingestion (CVP / MITC / Offers):**
   * Scheduled scrapers/watchers monitor issuer CVP pages, MITC PDFs, and offer portals (`firstrewards.in`, RuPay/Visa/MC offer hubs).
   * Documents are content-hashed; **LLM extraction triggers ONLY when a hash changes**, conserving tokens.
   * The LLM outputs a strict schema-validated **JSON Diff** tagged with `effective_from`, confidence score, and source citation. High-confidence diffs auto-stage into a lightweight human-in-the-loop approval queue—once confirmed, the updated rule immediately refreshes the Matrix, Spend Simulator, MITC badges in Command Center, and Event Pins in the Telemetry Overlay.

### 6.2 Proactive Intelligence & Anomaly Engine
Instead of forcing users to hunt across 5 modules for problems, run a daily/weekly rules + statistical engine that surfaces prioritized **Action Cards** in a global Notification / Briefing Drawer:
* **Silent Wallet-Migration Alerts:** *"BIN `65301510` 1M spend fell 38% vs. 3M avg while cardholders' total UPI wallet grew 6%—migrating to Savings UPI following the Utility 1% MITC fee."*
* **Offer ROI & Competitor Threat Alerts:** *"Mastercard's weekend Swiggy offer reduced RuPay share at Swiggy by 3.4pp in 10 days; current RuPay GMV at risk: ₹29 Cr/mo."*
* **MID Acceptance Leakage Alerts:** *"42 high-volume Large Offline MIDs (>₹2K avg) saw RuPay CC decline rates jump >18% (`errcode` cluster) while bank-account UPI stayed >98% approved."*
* **Deal Cliff & Milestone Alerts:** *"Issuer B is 3.2% away from crossing the 20L monthly volume cliff slab in M22 (projected −1.8 bps Net BPS impact)."*
* **Near-Cliff Activation Opportunities:** *"68,400 active Select cardholders are within ₹8,000 of their quarterly milestone with 14 days remaining."*

### 6.3 Grounded Conversational Analyst (Copilot Drawer)
Embed an optional slide-out **RuPay Intelligence Copilot** that answers ad-hoc strategic questions (*"Which Unsecured Co-Brand Select cards lost UPI Wallet Share after adding a lounge spend gate in the last 6 months, and how does that affect their Deal Net BPS?"*):
* **Strict Grounding:** Translates questions into read-only SQL against the locked `agg_*` Semantic Layer, reads versioned JSON from the Proposition Control Plane, and invokes the pure-math Simulator / Deal Engines—**zero hallucinated numbers**, with clickable SQL/formula citations and one-click "Pin to View" chart generation.

### 6.4 Closed-Loop Learning
* Live Deal actuals automatically feed back into the Deal Model's quant projection engine and quarterly meta-learning loop (re-tuning signal weights/magnitudes with automatic rollback if MAPE worsens).
* Post-offer `D+30` and `D+60` retention telemetry scores historical campaigns by category and payment mode (`FS` vs. `EMI`), automatically recommending optimal minimum-ticket and cap structures for future RuPay merchant campaigns.

---

## 7. GitHub-Native Monorepo & Monthly Token-Governance Plan

### 7.1 Contract-First Monorepo Structure
Never build the platform as a single monolithic file. Enforce this repository layout in GitHub so each monthly token budget touches only one bounded package:

```text
rupay-360-platform/
├── docs/
│   ├── rupay_360_master_reference_blueprint.md   # This document
│   ├── ARCHITECTURE_DECISIONS.md                 # ADR log for internal AI upgrades
│   ├── 01_Design_System_and_Shell.md             # Tokens, 3-tier filter spec, InfoCard
│   ├── 02_Trino_Semantic_Layer.md                # Curated whitelisted columns (max ~30/table)
│   └── internal-context/                         # Confidential internal docs (gitignored/private)
├── schemas/
│   ├── dim_card_bin_master.schema.json
│   ├── cvp_catalog.schema.json
│   ├── mitc_catalog.schema.json
│   ├── offers_catalog.schema.json
│   └── interchange_rules.schema.json
├── packages/
│   ├── shared-ui/          # Tailwind + shadcn/ui primitives, InfoCard (?), Theme, Formatters
│   ├── trino-sql/          # Materialized agg_* DDL + typed query builders
│   ├── deal-engine/        # Pure UI-free V1.1 + Part B math + Section 11 Vitest suite
│   ├── simulator-engine/   # Pure UI-free CVP + Offer - MITC calculator + unit tests
│   └── intelligence-jobs/  # Diff-based ingestion, DiD causal engine, anomaly alert workers
└── apps/
    ├── shell/              # Collapsible sidebar, Workspace switcher, WS1 Global Filter bar
    ├── tab-command/        # Workspace 1: Command Center
    ├── tab-economics/      # Workspace 1: Card Economics
    ├── tab-wallet/         # Workspace 1: Wallet Share
    ├── tab-proposition/    # Workspace 2: CVP/MITC/Offers/Simulator/Overlay (Own local filters)
    └── tab-deal/           # Workspace 3: 6-Sub-Tab Deal Performance (Own project switcher)
```

### 7.2 Recommended Monthly Incremental Rollout (Token-Budget Optimized)

| Cycle | Scope / Deliverable | Mandatory Acceptance Gate ("Done When") |
| :--- | :--- | :--- |
| **Phase 0 (Setup)** | **Internal Context Ingestion + Trino Semantic Discovery + Canonical Spine (`dim_card_bin_master`, `dim_merchant_master`)** | `02_Trino_Semantic_Layer.md` locked; 5 `agg_*` tables scheduled; all 5 discovery gaps (CIF, cross-rail key, EMI, Intl, confidential interchange) resolved & logged in `ADR.md`. |
| **Month 1** | **App Shell + 3-Tier Cascading Filters + Command Center** | Collapsible shell & Dark/Light themes live; WS1 global filters work with cascading child indicators & Reset; all 6 Command Center cuts (incl. India/World maps, Churn Cohorts, User Spend Slabs) query Trino `agg_*` cleanly. |
| **Month 2** | **Proposition Control Plane (Matrix + Spend Simulator + Offers Hub)** | Independent WS2 local filters (incl. RuPay/Visa/MC, Secured FD, FS vs. EMI); `simulator-engine` unit tests pass; Telemetry Reality Check joins live Trino User Spend Slabs; daily merchant lift connects to `agg_daily_bin_merchant`. |
| **Month 3** | **Card Economics (All Rails + UPI 2×2 + Real Interchange Engine + Acceptance Leakage)** | Confidential interchange schedules loaded via config layer; UPI 2×2 quadrants & `SLAB_D` × `errcode` cliffs reconcile to Trino; MID-level acceptance leakage tracker identifies opt-out merchants. |
| **Month 4** | **Multi-Rail Wallet Share + 3-Mode Telemetry Overlay + DiD Causal Engine** | Multi-rail Wallet Share drills down to MCC & Top-20 Merchants; Silent Wallet-Migration Radar active; 16-variant Sparkline Matrix & `T = 0` normalized DiD overlay pass backtest checks. |
| **Month 5** | **Deal Performance — Part A (Full V1.1 5-Tab Parity)** | Pure `deal-engine` ported directly from GitHub V1.1 source; **100% of Section 11 reference numbers match to 3 decimal places (`15.996` Net BPS)**; all 5 V1.1 sub-tabs, Trino Peer Seeding, and SheetJS exports work inside isolated WS3. |
| **Month 6** | **Deal Performance — Part B (Live Tracking + Trino Auto-Feed)** | Locked baselines (`deal_baselines`), Trino-fed `deal_actuals`, 3 re-forecast modes, dual upfront BPS, sequential revenue bridge, milestone rules (`cif` vs. `cif_spends`), and binary-search floor solver pass all Part B acceptance tests. |
| **Month 7+** | **Self-Updating Automation, Proactive Alert Engine & Grounded Copilot** | Hash-diff CVP/MITC/Offer ingestion pipeline live; automated anomaly/cliff briefing cards active; Copilot drawer answers cross-module questions via verified SQL & deterministic engines; AI Quant Signal loop integrated. |

### 7.3 Master Monthly Prompt Protocol (Copy-Paste for Internal Claude / ChatGPT)

```text
ROLE: Staff Analytics Engineer, Financial Systems Architect & Full-Stack Lead for the RuPay Network.

CONTEXT ACCESS:
- Repository: Read `/docs/rupay_360_master_reference_blueprint.md`, `/docs/ARCHITECTURE_DECISIONS.md`, `/docs/01_Design_System_and_Shell.md`, and `/docs/02_Trino_Semantic_Layer.md` from GitHub.
- Internal Context: Cross-reference the uploaded confidential documents in `/docs/internal-context/` and verify table/column assumptions directly against live Trino metadata before writing SQL.

DISCRETION & QUALITY RULE:
- If internal documents or live Trino data reveal more accurate rules, richer fields, or higher-impact cuts than the baseline blueprint, upgrade the design proactively and record the decision in `/docs/ARCHITECTURE_DECISIONS.md`.
- Write deterministic unit tests FIRST for any math/financial logic; never let an LLM approximate calculated metrics.
- Stay strictly within this cycle's target package so we stay well inside token limits and avoid regressions.

THIS MONTH'S TASK — [Month X: Package / Module Name]:
1. Confirm any schema or internal-doc deltas impacting this module and update `ADR.md` if needed.
2. Build/update the Trino SQL aggregation queries in `packages/trino-sql/` (using `dim_card_bin_master` — never inline BIN truncation).
3. Implement the pure logic + unit tests (if applicable) and verify all tests pass.
4. Build the isolated UI module in `apps/tab-[name]/` adhering strictly to Workspace filter isolation rules, shared formatters, and `?` audit breakdowns.
5. Output a concise summary of files created/modified, test results, and any open data-lake gaps discovered.
```