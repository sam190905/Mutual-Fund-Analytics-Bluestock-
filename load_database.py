"""
load_database.py
Day 2 — Task 5: Load all cleaned datasets into SQLite via SQLAlchemy
Output: data/db/bluestock_mf.db
"""

import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine, text

PROCESSED = "data/processed"
DB_DIR    = "data/db"
DB_PATH   = f"{DB_DIR}/bluestock_mf.db"
SCHEMA    = "sql/schema.sql"

os.makedirs(DB_DIR, exist_ok=True)

# Remove existing DB for a clean load
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Apply schema
print("Applying schema...")
with open(SCHEMA, "r") as f:
    schema_sql = f.read()

# Let SQLite parse the complete script. Splitting on semicolons and then
# skipping chunks that start with "--" also skips CREATE statements preceded
# by comments, leaving the indexes with no tables to reference.
with engine.begin() as conn:
    conn.connection.driver_connection.executescript(schema_sql)
print("✓ Schema applied\n")


def load(csv_file, table_name):
    path = f"{PROCESSED}/{csv_file}"
    if not os.path.exists(path):
        print(f"  ⚠ Not found: {path}")
        return
    df = pd.read_csv(path)
    df.to_sql(table_name, engine, if_exists="append", index=False)
    with engine.connect() as conn:
        db_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
    match = "✓" if db_count == len(df) else "⚠ MISMATCH"
    print(f"  {match} {table_name:<30} CSV: {len(df):>6}  DB: {db_count:>6}")


# ── dim_fund ─────────────────────────────────────────────────
print("Loading dimension tables...")
load("clean_01_fund_master.csv", "dim_fund")

# ── dim_date (generated from NAV date range) ─────────────────
print("\nGenerating dim_date...")
nav_df = pd.read_csv(f"{PROCESSED}/clean_02_nav_history.csv")
all_dates = pd.date_range(
    start=pd.to_datetime(nav_df["date"]).min(),
    end=pd.to_datetime(nav_df["date"]).max(),
    freq="D"
)
dim_date = pd.DataFrame({"date": all_dates})
dim_date["date_id"]    = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
dim_date["year"]       = dim_date["date"].dt.year
dim_date["month"]      = dim_date["date"].dt.month
dim_date["quarter"]    = dim_date["date"].dt.quarter
dim_date["month_name"] = dim_date["date"].dt.strftime("%B")
dim_date["is_weekday"] = (dim_date["date"].dt.dayofweek < 5).astype(int)
dim_date["date"]       = dim_date["date"].dt.strftime("%Y-%m-%d")
dim_date.to_sql("dim_date", engine, if_exists="append", index=False)
with engine.connect() as conn:
    c = conn.execute(text("SELECT COUNT(*) FROM dim_date")).scalar()
print(f"  ✓ dim_date                     Generated: {len(dim_date):>6}  DB: {c:>6}")

# ── fact_nav (compute daily_return_pct before loading) ───────
print("\nLoading fact tables...")
nav = pd.read_csv(f"{PROCESSED}/clean_02_nav_history.csv")
nav = nav.sort_values(["amfi_code", "date"]).reset_index(drop=True)
nav["daily_return_pct"] = (
    nav.groupby("amfi_code")["nav"]
       .pct_change()
       .round(6)
)
nav[["amfi_code", "date", "nav", "daily_return_pct"]].to_sql(
    "fact_nav", engine, if_exists="append", index=False
)
with engine.connect() as conn:
    c = conn.execute(text("SELECT COUNT(*) FROM fact_nav")).scalar()
print(f"  ✓ fact_nav                     CSV: {len(nav):>6}  DB: {c:>6}")

# ── remaining fact tables ─────────────────────────────────────
load("clean_08_investor_transactions.csv",  "fact_transactions")
load("clean_07_scheme_performance.csv",     "fact_performance")
load("clean_03_aum_by_fund_house.csv",      "fact_aum")
load("clean_04_monthly_sip_inflows.csv",    "fact_sip_industry")
load("clean_05_category_inflows.csv",       "fact_category_inflows")
load("clean_06_industry_folio_count.csv",   "fact_folio_count")
load("clean_09_portfolio_holdings.csv",     "fact_portfolio")
load("clean_10_benchmark_indices.csv",      "fact_benchmark")

# ── Summary ───────────────────────────────────────────────────
print("\n=== DATABASE SUMMARY ===")
tables = [
    "dim_fund", "dim_date", "fact_nav", "fact_transactions",
    "fact_performance", "fact_aum", "fact_sip_industry",
    "fact_category_inflows", "fact_folio_count",
    "fact_portfolio", "fact_benchmark"
]
with engine.connect() as conn:
    for t in tables:
        c = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        print(f"  {t:<35} {c:>8} rows")

print(f"\n✓ Database saved → {DB_PATH}")
