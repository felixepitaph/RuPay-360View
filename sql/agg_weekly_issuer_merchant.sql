-- Weekly spend by issuer, card product and canonical merchant. VERIFY ALL COLUMN NAMES IN PHASE 0.
-- Card rail and UPI CC are unioned; merchant identity comes from dim_merchant_master.
WITH txn AS (
  SELECT date_trunc('week', CAST({{txn_date_col}} AS date)) AS week_start,
         b.issuer_bank, b.card_id, {{merchant_key_card_rail}} AS merchant_key,
         {{amount_col}} AS amt, {{card_id_col}} AS card_ref
  FROM {{card_rail_table}} t
  JOIN {{dim_card_bin_master}} b ON {{bin_join_rule}}            -- 6 vs 8 digit rule lives in the dim table
  WHERE {{approved_flag_condition}} AND b.issuer_bank IN ('YES BANK', 'IDFC FIRST Bank')
    AND CAST({{txn_date_col}} AS date) >= current_date - INTERVAL '70' DAY
  UNION ALL
  SELECT date_trunc('week', CAST({{upi_date_col}} AS date)), b.issuer_bank, b.card_id,
         st.payeemerchantbrand, txnamount, {{upi_card_ref_col}}
  FROM {{upi_cc_table}} u
  JOIN {{dim_card_bin_master}} b ON {{upi_bin_join_rule}}
  WHERE {{upi_approved_condition}} AND b.issuer_bank IN ('YES BANK', 'IDFC FIRST Bank')
    AND CAST({{upi_date_col}} AS date) >= current_date - INTERVAL '70' DAY
)
SELECT t.week_start, t.issuer_bank, t.card_id, m.merchant_id, m.category,
       SUM(t.amt) AS spend, COUNT(*) AS txns, COUNT(DISTINCT t.card_ref) AS cards
FROM txn t
JOIN {{dim_merchant_master}} m ON lower(t.merchant_key) = lower(m.merchant_key)
GROUP BY 1, 2, 3, 4, 5
