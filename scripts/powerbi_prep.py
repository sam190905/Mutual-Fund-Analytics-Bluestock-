"""
powerbi_prep.py
Prepares all data files optimised for Power BI import.
Run this before opening Power BI Desktop.
Outputs flat CSVs to data/powerbi/ with clean column names and no index columns.
"""

import pandas as pd
import numpy as np
import os
from paths import POWERBI_DIR, RAW_DIR, REPORTS_DIR

POWERBI_DIR.mkdir(parents=True, exist_ok=True)

# ── 1. dim_fund ───────────────────────────────────────────────
fm = pd.read_csv(RAW_DIR / "01_fund_master.csv")
fm.to_csv(POWERBI_DIR / "dim_fund.csv", index=False)
print(f"✓ dim_fund.csv          {fm.shape}")

# ── 2. fact_nav (with daily return) ───────────────────────────
nav = pd.read_csv(RAW_DIR / "02_nav_history.csv", parse_dates=["date"])
nav = nav.sort_values(["amfi_code","date"])
nav["daily_return_pct"] = nav.groupby("amfi_code")["nav"].pct_change().round(6)
nav["date"] = nav["date"].dt.strftime("%Y-%m-%d")
nav.to_csv(POWERBI_DIR / "fact_nav.csv", index=False)
print(f"✓ fact_nav.csv          {nav.shape}")

# ── 3. fact_aum ───────────────────────────────────────────────
aum = pd.read_csv(RAW_DIR / "03_aum_by_fund_house.csv", parse_dates=["date"])
aum["year"] = aum["date"].dt.year
aum["date"] = aum["date"].dt.strftime("%Y-%m-%d")
aum.to_csv(POWERBI_DIR / "fact_aum.csv", index=False)
print(f"✓ fact_aum.csv          {aum.shape}")

# ── 4. fact_sip ───────────────────────────────────────────────
sip = pd.read_csv(RAW_DIR / "04_monthly_sip_inflows.csv")
sip["date"] = pd.to_datetime(sip["month"]).dt.strftime("%Y-%m-%d")
sip.to_csv(POWERBI_DIR / "fact_sip_industry.csv", index=False)
print(f"✓ fact_sip_industry.csv {sip.shape}")

# ── 5. fact_category_inflows ──────────────────────────────────
cat = pd.read_csv(RAW_DIR / "05_category_inflows.csv")
cat["date"] = pd.to_datetime(cat["month"]).dt.strftime("%Y-%m-%d")
cat.to_csv(POWERBI_DIR / "fact_category_inflows.csv", index=False)
print(f"✓ fact_category_inflows {cat.shape}")

# ── 6. fact_folio ─────────────────────────────────────────────
folio = pd.read_csv(RAW_DIR / "06_industry_folio_count.csv")
folio["date"] = pd.to_datetime(folio["month"]).dt.strftime("%Y-%m-%d")
folio.to_csv(POWERBI_DIR / "fact_folio_count.csv", index=False)
print(f"✓ fact_folio_count.csv  {folio.shape}")

# ── 7. fact_performance ───────────────────────────────────────
perf = pd.read_csv(RAW_DIR / "07_scheme_performance.csv")

# Merge scorecard if it exists
scorecard_path = REPORTS_DIR / "fund_scorecard.csv"
if scorecard_path.exists():
    sc = pd.read_csv(scorecard_path)[["amfi_code","composite_score","overall_rank"]]
    perf = perf.merge(sc, on="amfi_code", how="left")
    print("  ↳ Scorecard merged into fact_performance")

perf.to_csv(POWERBI_DIR / "fact_performance.csv", index=False)
print(f"✓ fact_performance.csv  {perf.shape}")

# ── 8. fact_transactions ──────────────────────────────────────
tx = pd.read_csv(RAW_DIR / "08_investor_transactions.csv", parse_dates=["transaction_date"])
tx["transaction_date"] = tx["transaction_date"].dt.strftime("%Y-%m-%d")
tx["month"] = pd.to_datetime(tx["transaction_date"]).dt.strftime("%Y-%m")
tx["amount_crore"] = (tx["amount_inr"] / 1e7).round(4)
tx.to_csv(POWERBI_DIR / "fact_transactions.csv", index=False)
print(f"✓ fact_transactions.csv {tx.shape}")

# ── 9. fact_portfolio ─────────────────────────────────────────
port = pd.read_csv(RAW_DIR / "09_portfolio_holdings.csv")
port.to_csv(POWERBI_DIR / "fact_portfolio.csv", index=False)
print(f"✓ fact_portfolio.csv    {port.shape}")

# ── 10. fact_benchmark ────────────────────────────────────────
bench = pd.read_csv(RAW_DIR / "10_benchmark_indices.csv", parse_dates=["date"])
bench["date"] = bench["date"].dt.strftime("%Y-%m-%d")
bench.to_csv(POWERBI_DIR / "fact_benchmark.csv", index=False)
print(f"✓ fact_benchmark.csv    {bench.shape}")

# ── 11. dim_date ──────────────────────────────────────────────
all_dates = pd.date_range(start="2022-01-01", end="2026-05-31", freq="D")
dim_date = pd.DataFrame({
    "date"      : all_dates.strftime("%Y-%m-%d"),
    "year"      : all_dates.year,
    "month_num" : all_dates.month,
    "month_name": all_dates.strftime("%B"),
    "quarter"   : all_dates.quarter,
    "quarter_label": "Q" + all_dates.quarter.astype(str) + " " + all_dates.year.astype(str),
    "is_weekday": (all_dates.dayofweek < 5).astype(int),
    "month_year": all_dates.strftime("%b %Y"),
})
dim_date.to_csv(POWERBI_DIR / "dim_date.csv", index=False)
print(f"✓ dim_date.csv          {dim_date.shape}")

# ── KPI summary for Page 1 cards ──────────────────────────────
kpi = pd.DataFrame([
    {"metric": "Total Industry AUM (₹ Lakh Crore)", "value": 81.0,    "as_of": "Dec 2025"},
    {"metric": "Monthly SIP Inflow (₹ Crore)",      "value": 31002,   "as_of": "Dec 2025"},
    {"metric": "Total Folios (Crore)",               "value": 26.12,   "as_of": "Dec 2025"},
    {"metric": "Active SIP Accounts (Crore)",        "value": 9.35,    "as_of": "Dec 2025"},
    {"metric": "Total Schemes",                      "value": 1908,    "as_of": "Dec 2025"},
    {"metric": "Schemes in Dataset",                 "value": 40,      "as_of": "Dec 2025"},
])
kpi.to_csv(POWERBI_DIR / "kpi_summary.csv", index=False)
print(f"✓ kpi_summary.csv       {kpi.shape}")

print(f"\n✓ All Power BI files saved → data/powerbi/")
print(f"  Total files: {len(list(POWERBI_DIR.iterdir()))}")
