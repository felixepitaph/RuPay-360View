-- Weekly spend per card and merchant with a SALTED HASH card key. VERIFY COLUMN NAMES IN PHASE 0.
-- The salt is a secret set by the data team; the key is only ever used inside aggregate queries
-- (data_access.py refuses any result column named card_key).
SELECT date_trunc('week', CAST({{txn_date_col}} AS date)) AS week_start,
       to_hex(sha256(to_utf8(concat('{{salt}}', CAST({{card_id_col}} AS varchar))))) AS card_key,
       b.issuer_bank, b.card_id, m.merchant_id, m.category, SUM({{amount_col}}) AS spend
FROM {{card_rail_table}} t
JOIN {{dim_card_bin_master}} b ON {{bin_join_rule}}
JOIN {{dim_merchant_master}} m ON lower({{merchant_key_card_rail}}) = lower(m.merchant_key)
WHERE {{approved_flag_condition}} AND CAST({{txn_date_col}} AS date) >= current_date - INTERVAL '70' DAY
GROUP BY 1, 2, 3, 4, 5, 6
