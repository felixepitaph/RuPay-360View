"""Builds SYNTHETIC data for the end-to-end demo. Nothing here is real. Planted story:
  * IDFC FIRST runs a flat Rs150 off (min Rs999, full swipe) offer at Zepto, 1-7 Jan 2027.
  * IDFC cardholders who usually shop at Blinkit move about a quarter of that spend to Zepto that week.
  * YES BANK cards see a Swiggy drop the same week with NO catalogued cause (should stay unexplained).
  * Oct-Nov festive uplift for everyone (seasonal noise the Watcher must not over-read).
Run:  python demo/make_synthetic.py
"""
import datetime as dt
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)
WEEKS = [dt.date(2026, 10, 5) + dt.timedelta(weeks=i) for i in range(15)]  # to week of 2027-01-11
OFFER_WEEK = dt.date(2027, 1, 4)
ISSUERS = {"IDFC FIRST Bank": ["IDFC_FIRST_MILLENNIA", "IDFC_FIRST_WEALTH"],
           "YES BANK": ["YES_ACE", "YES_ELITE_PLUS"],
           "OTHER ISSUERS (control)": ["OTHER_RUPAY_CARDS"]}
CAT = {"BLINKIT": "QUICK_COMMERCE", "ZEPTO": "QUICK_COMMERCE", "BIGBASKET": "QUICK_COMMERCE",
       "SWIGGY": "FOOD_DELIVERY", "ZOMATO": "FOOD_DELIVERY"}
N_CARDS = 5000



def _save(df, name):
    import duckdb  # writes parquet without needing pyarrow
    duckdb.register("df_view", df)
    duckdb.execute(f"COPY (SELECT * REPLACE (CAST(week_start AS DATE) AS week_start) FROM df_view) TO '{(OUT / name).as_posix()}.parquet' (FORMAT PARQUET)")
    duckdb.unregister("df_view")


rows = []
for iss, cards in ISSUERS.items():
    for k in range(N_CARDS):
        key = hashlib.sha256(f"salt|{iss}|{k}".encode()).hexdigest()[:16]
        card_id = cards[k % len(cards)]
        qc = rng.choice(["BLINKIT", "ZEPTO", "BIGBASKET"], p=[.5, .3, .2])
        food = rng.choice(["SWIGGY", "ZOMATO"], p=[.55, .45])
        qc_amt = rng.gamma(2.0, 450)
        food_amt = rng.gamma(2.0, 350)
        for w in WEEKS:
            fest = 1.15 if dt.date(2026, 10, 12) <= w <= dt.date(2026, 11, 9) else 1.0
            noise = rng.normal(1, .12)
            spend = {qc: qc_amt * fest * noise, food: food_amt * fest * rng.normal(1, .12)}
            if w == OFFER_WEEK and iss == "IDFC FIRST Bank" and qc == "BLINKIT" and rng.random() < .45:
                moved = spend["BLINKIT"] * .55
                spend["BLINKIT"] -= moved
                spend["ZEPTO"] = spend.get("ZEPTO", 0) + moved * 1.05
            if w == OFFER_WEEK and iss == "YES BANK" and food == "SWIGGY" and rng.random() < .4:
                spend["SWIGGY"] *= .35
            for m, s in spend.items():
                if s > 0 and rng.random() > .08:
                    rows.append((w, key, iss, card_id, m, CAT[m], round(max(s, 0), 2)))

t = pd.DataFrame(rows, columns=["week_start", "card_key", "issuer_bank", "card_id", "merchant_id", "category", "spend"])
t["week_start"] = pd.to_datetime(t["week_start"])
_save(t, "txn_weekly_card_merchant")
agg = (t.groupby(["week_start", "issuer_bank", "card_id", "merchant_id", "category"], as_index=False)
        .agg(spend=("spend", "sum"), txns=("spend", "size"), cards=("card_key", "nunique")))
_save(agg, "agg_weekly_issuer_merchant")
print(f"{len(t):,} card-week rows, {len(agg):,} aggregate rows -> {OUT}")
