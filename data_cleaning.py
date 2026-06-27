"""
data_cleaning.py
Day 2 — Tasks 1, 2, 3: Clean nav_history, investor_transactions, scheme_performance
Output: cleaned CSVs saved to data/processed/
"""

import pandas as pd
import numpy as np
import os

RAW       = "data/raw"
PROCESSED = "data/processed"
os.makedirs(PROCESSED, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# TASK 1 — Clean 02_nav_history.csv
# Columns: amfi_code (int), date (str YYYY-MM-DD), nav (float)
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("TASK 1: Cleaning 02_nav_history.csv")
print("="*60)

nav = pd.read_csv(f"{RAW}/02_nav_history.csv")
print(f"Raw shape      : {nav.shape}")

# 1a. Parse date — already YYYY-MM-DD, just cast to datetime
nav["date"] = pd.to_datetime(nav["date"], format="%Y-%m-%d", errors="coerce")
bad_dates = nav["date"].isna().sum()
if bad_dates:
    print(f"Invalid dates dropped: {bad_dates}")
    nav = nav.dropna(subset=["date"])

# 1b. No duplicates found (confirmed), but run anyway
before = len(nav)
nav = nav.drop_duplicates(subset=["amfi_code", "date"])
print(f"Duplicates removed : {before - len(nav)}")

# 1c. Sort by amfi_code + date
nav = nav.sort_values(["amfi_code", "date"]).reset_index(drop=True)

# 1d. Validate NAV > 0 — all clean (confirmed), keep check for safety
invalid_nav = (nav["nav"] <= 0).sum()
print(f"NAV <= 0 rows      : {invalid_nav}")
nav = nav[nav["nav"] > 0]

# 1e. Forward-fill missing NAV for weekends/holidays
#     Reindex each fund to a full daily date range, then ffill
filled = []
for code, group in nav.groupby("amfi_code"):
    group = group.set_index("date")
    full_range = pd.date_range(start=group.index.min(), end=group.index.max(), freq="D")
    group = group.reindex(full_range)
    group["amfi_code"] = code
    group["nav"] = group["nav"].ffill()
    group.index.name = "date"
    filled.append(group.reset_index())

nav_clean = pd.concat(filled, ignore_index=True)
nav_clean = nav_clean.dropna(subset=["nav"])
nav_clean["date"] = nav_clean["date"].dt.strftime("%Y-%m-%d")

print(f"Clean shape        : {nav_clean.shape}")
nav_clean.to_csv(f"{PROCESSED}/clean_02_nav_history.csv", index=False)
print(f"✓ Saved → data/processed/clean_02_nav_history.csv")


# ─────────────────────────────────────────────────────────────
# TASK 2 — Clean 08_investor_transactions.csv
# Columns: investor_id, transaction_date, amfi_code, transaction_type,
#          amount_inr, state, city, city_tier, age_group, gender,
#          annual_income_lakh, payment_mode, kyc_status
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("TASK 2: Cleaning 08_investor_transactions.csv")
print("="*60)

tx = pd.read_csv(f"{RAW}/08_investor_transactions.csv")
print(f"Raw shape          : {tx.shape}")

# 2a. Standardise transaction_type — already clean (SIP/Lumpsum/Redemption confirmed)
print(f"transaction_type values: {tx['transaction_type'].unique().tolist()}")
valid_types = ["SIP", "Lumpsum", "Redemption"]
invalid_type = tx[~tx["transaction_type"].isin(valid_types)]
if len(invalid_type) > 0:
    print(f"⚠ Invalid transaction_type rows: {len(invalid_type)}")
    tx = tx[tx["transaction_type"].isin(valid_types)]

# 2b. Parse date — already YYYY-MM-DD
tx["transaction_date"] = pd.to_datetime(tx["transaction_date"], format="%Y-%m-%d", errors="coerce")
bad_dates = tx["transaction_date"].isna().sum()
if bad_dates:
    print(f"Invalid dates dropped: {bad_dates}")
    tx = tx.dropna(subset=["transaction_date"])

# 2c. Validate amount > 0 — confirmed clean, keep check
invalid_amt = (tx["amount_inr"] <= 0).sum()
print(f"amount_inr <= 0    : {invalid_amt}")
tx = tx[tx["amount_inr"] > 0]

# 2d. Validate KYC status — Verified / Pending confirmed
print(f"kyc_status values  : {tx['kyc_status'].unique().tolist()}")
valid_kyc = ["Verified", "Pending"]
invalid_kyc = tx[~tx["kyc_status"].isin(valid_kyc)]
if len(invalid_kyc) > 0:
    print(f"Invalid KYC rows: {len(invalid_kyc)}")

# 2e. Duplicates — confirmed 0, run anyway
before = len(tx)
tx = tx.drop_duplicates()
print(f"Duplicates removed : {before - len(tx)}")

# 2f. Format date back to string for CSV
tx["transaction_date"] = tx["transaction_date"].dt.strftime("%Y-%m-%d")

print(f"Clean shape        : {tx.shape}")
tx.to_csv(f"{PROCESSED}/clean_08_investor_transactions.csv", index=False)
print(f"✓ Saved → data/processed/clean_08_investor_transactions.csv")


# ─────────────────────────────────────────────────────────────
# TASK 3 — Clean 07_scheme_performance.csv
# Columns: amfi_code, scheme_name, fund_house, category, plan,
#          return_1yr_pct, return_3yr_pct, return_5yr_pct,
#          benchmark_3yr_pct, alpha, beta, sharpe_ratio,
#          sortino_ratio, std_dev_ann_pct, max_drawdown_pct,
#          aum_crore, expense_ratio_pct, morningstar_rating, risk_grade
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("TASK 3: Cleaning 07_scheme_performance.csv")
print("="*60)

perf = pd.read_csv(f"{RAW}/07_scheme_performance.csv")
print(f"Raw shape          : {perf.shape}")

# 3a. Ensure all return/metric columns are numeric
metric_cols = [
    "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio",
    "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct",
    "aum_crore", "expense_ratio_pct"
]
for col in metric_cols:
    if col in perf.columns:
        before_nulls = perf[col].isna().sum()
        perf[col] = pd.to_numeric(perf[col], errors="coerce")
        after_nulls = perf[col].isna().sum()
        if after_nulls > before_nulls:
            print(f" {col}: {after_nulls - before_nulls} values coerced to NaN")

# 3b. Flag anomalies (log only, do not drop — 40 rows, every row is valuable)
print("\n--- Anomaly Flags ---")

neg_sharpe = perf[perf["sharpe_ratio"] < 0]
print(f"Negative Sharpe ratio     : {len(neg_sharpe)} funds")

extreme_1yr = perf[(perf["return_1yr_pct"] > 100) | (perf["return_1yr_pct"] < -50)]
print(f"Extreme 1yr returns       : {len(extreme_1yr)} funds")

# max_drawdown should be negative (confirmed range: -33.5 to -2.23)
positive_dd = perf[perf["max_drawdown_pct"] > 0]
print(f"Positive max_drawdown     : {len(positive_dd)} funds (should all be negative)")

# 3c. Validate expense_ratio range 0.1% – 2.5%
# Actual range confirmed: 0.55 – 1.64 (all within bounds)
out_of_range = perf[
    (perf["expense_ratio_pct"] < 0.1) | (perf["expense_ratio_pct"] > 2.5)
]
print(f"Expense ratio out of range: {len(out_of_range)} funds")
print(f"  Actual range: {perf['expense_ratio_pct'].min()} – {perf['expense_ratio_pct'].max()}")

# 3d. Validate risk_grade enum
valid_risk = ["Low", "Moderate", "Moderately High", "High", "Very High"]
invalid_risk = perf[~perf["risk_grade"].isin(valid_risk)]
print(f"Invalid risk_grade values : {len(invalid_risk)}")

print(f"\nClean shape        : {perf.shape}")
perf.to_csv(f"{PROCESSED}/clean_07_scheme_performance.csv", index=False)
print(f"✓ Saved → data/processed/clean_07_scheme_performance.csv")


# ─────────────────────────────────────────────────────────────
# Copy remaining 7 CSVs to processed/ with clean_ prefix
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("Copying remaining datasets to processed/")
print("="*60)

others = [
    "01_fund_master.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]

for fname in others:
    src = f"{RAW}/{fname}"
    if os.path.exists(src):
        df = pd.read_csv(src)
        out = f"{PROCESSED}/clean_{fname}"
        df.to_csv(out, index=False)
        print(f"   {fname:<35} {str(df.shape)}")
    else:
        print(f"   Not found: {src}")

print("\n All cleaning complete.")
print(f"\nFiles in data/processed/:")
for f in sorted(os.listdir(PROCESSED)):
    print(f"  {f}")