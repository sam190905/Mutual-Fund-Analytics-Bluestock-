# Data Dictionary
## Bluestock Fintech — Mutual Fund Analytics Capstone
**Day 2 Deliverable** | Source: 10 provided CSVs + mfapi.in

---

## 01_fund_master.csv → `dim_fund` (40 rows)

| Column | Type | Description | Example |
|---|---|---|---|
| `amfi_code` | INTEGER (PK) | Unique AMFI scheme code. Direct & Regular plans have separate codes. | `119551` |
| `fund_house` | TEXT | Asset Management Company name | `SBI Mutual Fund` |
| `scheme_name` | TEXT | Full official AMFI scheme name | `SBI Bluechip Fund - Direct Plan` |
| `category` | TEXT | Broad SEBI category | `Equity`, `Debt`, `Hybrid` |
| `sub_category` | TEXT | SEBI sub-category | `Large Cap`, `Mid Cap`, `Small Cap` |
| `plan` | TEXT | Plan type | `Direct`, `Regular` |
| `launch_date` | TEXT | Scheme launch date (YYYY-MM-DD) | `2013-01-01` |
| `benchmark` | TEXT | Official benchmark index | `Nifty 100 TRI` |
| `expense_ratio_pct` | REAL | Annual TER in % (range: 0.55–1.64) | `0.85` |
| `exit_load_pct` | REAL | Exit load % on early redemption | `1.0` |
| `min_sip_amount` | INTEGER | Minimum SIP instalment in Rs. | `500` |
| `min_lumpsum_amount` | INTEGER | Minimum lump-sum investment in Rs. | `5000` |
| `fund_manager` | TEXT | Primary fund manager name | `Dinesh Balachandran` |
| `risk_category` | TEXT | SEBI risk label | `Low`, `Moderate`, `High`, `Very High` |
| `sebi_category_code` | TEXT | SEBI internal code: EC01=LargeCap, EC03=SmallCap, DC01=Liquid | `EC01` |

---

## 02_nav_history.csv → `fact_nav` (46,000 rows → ~65,000 after ffill)

| Column | Type | Description | Example |
|---|---|---|---|
| `amfi_code` | INTEGER (FK) | References dim_fund | `119551` |
| `date` | TEXT | NAV date YYYY-MM-DD. Business days only in source; weekends forward-filled. | `2024-01-15` |
| `nav` | REAL | Net Asset Value in Rs. All values > 0. | `54.3856` |
| `daily_return_pct` | REAL | Computed: `(nav_t / nav_t-1) - 1`. NULL for first row of each fund. | `0.002341` |

---

## 03_aum_by_fund_house.csv → `fact_aum` (90 rows)

| Column | Type | Description | Example |
|---|---|---|---|
| `date` | TEXT | Quarter-end date YYYY-MM-DD | `2025-12-31` |
| `fund_house` | TEXT | AMC name (10 fund houses) | `SBI Mutual Fund` |
| `aum_lakh_crore` | REAL | AUM in Rs. lakh crore | `12.50` |
| `aum_crore` | INTEGER | AUM in Rs. crore | `1250000` |
| `num_schemes` | INTEGER | Number of active schemes | `186` |

**Note:** SBI MF Dec 2025 AUM = Rs. 12.50 lakh crore (largest in India).

---

## 04_monthly_sip_inflows.csv → `fact_sip_industry` (48 rows)

| Column | Type | Description | Example |
|---|---|---|---|
| `month` | TEXT | YYYY-MM format | `2025-12` |
| `sip_inflow_crore` | INTEGER | Monthly SIP inflows in Rs. crore | `31002` |
| `active_sip_accounts_crore` | REAL | Active SIP accounts in crore | `9.35` |
| `new_sip_accounts_lakh` | REAL | New SIP registrations (lakh) | `48.2` |
| `sip_aum_lakh_crore` | REAL | Total SIP AUM in Rs. lakh crore | `13.4` |
| `yoy_growth_pct` | REAL | YoY growth in SIP inflows (%). NULL for first 12 months. | `22.5` |

**Milestone:** Dec 2025 = Rs. 31,002 crore (all-time high).

---

## 05_category_inflows.csv → `fact_category_inflows` (144 rows)

| Column | Type | Description | Example |
|---|---|---|---|
| `month` | TEXT | YYYY-MM | `2024-04` |
| `category` | TEXT | Fund category | `Large Cap`, `Mid Cap`, `Small Cap`, `ELSS`, `Liquid` |
| `net_inflow_crore` | REAL | Net inflows in Rs. crore (negative = net outflow) | `2413.0` |

---

## 06_industry_folio_count.csv → `fact_folio_count` (21 rows)

| Column | Type | Description | Example |
|---|---|---|---|
| `month` | TEXT | YYYY-MM (quarterly observations) | `2022-01` |
| `total_folios_crore` | REAL | Total MF folios in crore | `26.12` |
| `equity_folios_crore` | REAL | Equity segment folios | `19.84` |
| `debt_folios_crore` | REAL | Debt segment folios | `3.26` |
| `hybrid_folios_crore` | REAL | Hybrid segment folios | `0.80` |
| `others_folios_crore` | REAL | Others (ETF, FoF, etc.) | `1.33` |

---

## 07_scheme_performance.csv → `fact_performance` (40 rows)

| Column | Type | Description | Example |
|---|---|---|---|
| `amfi_code` | INTEGER (PK/FK) | References dim_fund | `119551` |
| `scheme_name` | TEXT | Scheme name | `SBI Bluechip Fund` |
| `fund_house` | TEXT | AMC name | `SBI Mutual Fund` |
| `category` | TEXT | Broad category | `Equity` |
| `plan` | TEXT | Direct / Regular | `Direct` |
| `return_1yr_pct` | REAL | 1-year absolute return % | `18.5` |
| `return_3yr_pct` | REAL | 3-year CAGR % | `14.2` |
| `return_5yr_pct` | REAL | 5-year CAGR % | `16.8` |
| `benchmark_3yr_pct` | REAL | Benchmark 3yr CAGR % | `12.1` |
| `alpha` | REAL | `return_3yr - benchmark_3yr` | `2.1` |
| `beta` | REAL | Market sensitivity (1.0 = market). Range observed: 0.7–1.2 | `0.92` |
| `sharpe_ratio` | REAL | `(Rp - Rf) / StdDev`, Rf=6.5%. Range: 0.8–7.68 | `1.24` |
| `sortino_ratio` | REAL | Sharpe using only downside volatility | `1.67` |
| `std_dev_ann_pct` | REAL | Annualised standard deviation of daily returns % | `14.3` |
| `max_drawdown_pct` | REAL | Worst peak-to-trough decline. All values negative. Range: -33.5 to -2.23 | `-18.2` |
| `aum_crore` | INTEGER | Fund AUM in Rs. crore | `45000` |
| `expense_ratio_pct` | REAL | TER %. Range: 0.55–1.64 (all within SEBI 0.1–2.5% limits) | `0.85` |
| `morningstar_rating` | INTEGER | 1–5 stars (simulated from Sharpe percentile) | `4` |
| `risk_grade` | TEXT | `Low`, `Moderate`, `Moderately High`, `High`, `Very High` | `Moderate` |

---

## 08_investor_transactions.csv → `fact_transactions` (32,778 rows)

| Column | Type | Description | Example |
|---|---|---|---|
| `investor_id` | TEXT | Unique investor ID (INV000001–INV005000) | `INV003054` |
| `transaction_date` | TEXT | Date YYYY-MM-DD | `2024-01-01` |
| `amfi_code` | INTEGER (FK) | Fund invested in | `119551` |
| `transaction_type` | TEXT | `SIP`, `Lumpsum`, or `Redemption` | `SIP` |
| `amount_inr` | INTEGER | Transaction amount in Rs. All > 0. | `5000` |
| `state` | TEXT | Investor's Indian state | `Maharashtra` |
| `city` | TEXT | Investor's city | `Mumbai` |
| `city_tier` | TEXT | `T30` (Top 30 cities) or `B30` (Beyond Top 30) | `T30` |
| `age_group` | TEXT | `18-25`, `26-35`, `36-45`, `46-55`, `56+` | `26-35` |
| `gender` | TEXT | `Male` or `Female` | `Female` |
| `annual_income_lakh` | REAL | Annual income in Rs. lakh | `12.5` |
| `payment_mode` | TEXT | `UPI`, `Net Banking`, `Mandate`, `Cheque` | `UPI` |
| `kyc_status` | TEXT | `Verified` (92%) or `Pending` (8%) | `Verified` |

---

## 09_portfolio_holdings.csv → `fact_portfolio` (322 rows)

| Column | Type | Description | Example |
|---|---|---|---|
| `amfi_code` | INTEGER (FK) | References dim_fund | `119551` |
| `stock_symbol` | TEXT | NSE ticker symbol | `HDFCBANK` |
| `stock_name` | TEXT | Full company name | `HDFC Bank Ltd` |
| `sector` | TEXT | SEBI sector classification | `Financial Services` |
| `weight_pct` | REAL | Portfolio weight as % of fund AUM | `8.5` |
| `market_value_cr` | REAL | Market value of holding in Rs. crore | `3825.0` |
| `current_price_inr` | REAL | Stock price on portfolio_date | `1074.65` |
| `portfolio_date` | TEXT | Holdings disclosure date. All rows: `2025-12-31` | `2025-12-31` |

---

## 10_benchmark_indices.csv → `fact_benchmark` (8,050 rows)

| Column | Type | Description | Example |
|---|---|---|---|
| `date` | TEXT | Trading date YYYY-MM-DD | `2022-01-03` |
| `index_name` | TEXT | Index identifier | `NIFTY50`, `NIFTY100`, `NIFTY_MIDCAP150`, `BSE_SMALLCAP`, `NIFTY500`, `CRISIL_LIQUID`, `CRISIL_GILT` |
| `close_value` | REAL | Index closing value | `17492.79` |

---

## Data Sources

| Source | URL | Data Provided |
|---|---|---|
| AMFI India | www.amfiindia.com | NAV, AUM, Folio, SIP |
| mfapi.in | api.mfapi.in/mf/{code} | Historical NAV JSON |
| NSE India | nseindia.com | Nifty index prices |
| BSE India | bseindia.com | BSE SmallCap index |
| AMFI Monthly Notes | amfiindia.com/research | SIP flow data |


