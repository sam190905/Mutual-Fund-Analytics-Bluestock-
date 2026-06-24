-- ============================================================
-- queries.sql
-- Bluestock MF Analytics — 10 Analytical SQL Queries
-- Day 2: SQL Analytics
-- ============================================================


-- QUERY 1: Top 5 fund houses by latest AUM
SELECT
    fund_house,
    aum_lakh_crore,
    aum_crore,
    num_schemes,
    date
FROM fact_aum
WHERE date = (SELECT MAX(date) FROM fact_aum)
ORDER BY aum_crore DESC
LIMIT 5;


-- QUERY 2: Average NAV per month per fund (last 12 months)
SELECT
    n.amfi_code,
    f.scheme_name,
    f.fund_house,
    SUBSTR(n.date, 1, 7)            AS month,
    ROUND(AVG(n.nav), 2)            AS avg_nav,
    ROUND(MIN(n.nav), 2)            AS min_nav,
    ROUND(MAX(n.nav), 2)            AS max_nav
FROM fact_nav n
JOIN dim_fund f ON f.amfi_code = n.amfi_code
WHERE n.date >= DATE('now', '-12 months')
GROUP BY n.amfi_code, month
ORDER BY n.amfi_code, month;


-- QUERY 3: SIP inflow year-over-year growth
SELECT
    SUBSTR(month, 1, 4)                 AS year,
    ROUND(SUM(sip_inflow_crore), 0)     AS total_sip_crore,
    ROUND(AVG(active_sip_accounts_crore), 2) AS avg_active_accounts_crore,
    ROUND(AVG(yoy_growth_pct), 1)       AS avg_yoy_growth_pct
FROM fact_sip_industry
GROUP BY year
ORDER BY year;


-- QUERY 4: Total transaction amount by state and city tier
SELECT
    state,
    city_tier,
    COUNT(*)                            AS num_transactions,
    COUNT(DISTINCT investor_id)         AS unique_investors,
    ROUND(SUM(amount_inr) / 1e7, 2)    AS total_crore,
    ROUND(AVG(amount_inr), 0)          AS avg_amount_inr
FROM fact_transactions
GROUP BY state, city_tier
ORDER BY total_crore DESC;


-- QUERY 5: Funds with expense_ratio < 1% (cost-efficient schemes)
SELECT
    amfi_code,
    fund_house,
    scheme_name,
    sub_category,
    plan,
    expense_ratio_pct,
    risk_category
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;


-- QUERY 6: Top 10 funds by 3-year CAGR with alpha vs benchmark
SELECT
    p.amfi_code,
    p.scheme_name,
    p.fund_house,
    p.category,
    ROUND(p.return_3yr_pct, 2)      AS return_3yr_pct,
    ROUND(p.benchmark_3yr_pct, 2)   AS benchmark_3yr_pct,
    ROUND(p.alpha, 2)               AS alpha,
    ROUND(p.sharpe_ratio, 2)        AS sharpe_ratio,
    p.morningstar_rating
FROM fact_performance p
ORDER BY p.return_3yr_pct DESC
LIMIT 10;


-- QUERY 7: SIP vs Lumpsum vs Redemption split
SELECT
    transaction_type,
    COUNT(*)                            AS num_transactions,
    COUNT(DISTINCT investor_id)         AS unique_investors,
    ROUND(SUM(amount_inr) / 1e7, 2)    AS total_crore,
    ROUND(AVG(amount_inr), 0)          AS avg_amount_inr
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_crore DESC;


-- QUERY 8: Monthly SIP volume and inflow trend
SELECT
    SUBSTR(transaction_date, 1, 7)      AS month,
    COUNT(*)                            AS sip_count,
    COUNT(DISTINCT investor_id)         AS active_investors,
    ROUND(SUM(amount_inr) / 1e7, 2)    AS sip_inflow_crore
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY month
ORDER BY month;


-- QUERY 9: Fund ranking by Sharpe ratio within each sub-category
SELECT
    f.sub_category,
    p.scheme_name,
    p.fund_house,
    ROUND(p.sharpe_ratio, 2)        AS sharpe_ratio,
    ROUND(p.return_3yr_pct, 2)      AS return_3yr_pct,
    ROUND(p.max_drawdown_pct, 2)    AS max_drawdown_pct,
    RANK() OVER (
        PARTITION BY f.sub_category
        ORDER BY p.sharpe_ratio DESC
    )                               AS rank_in_category
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
ORDER BY f.sub_category, rank_in_category;


-- QUERY 10: AUM growth per fund house year-over-year
SELECT
    fund_house,
    SUBSTR(date, 1, 4)                  AS year,
    ROUND(MAX(aum_lakh_crore), 2)       AS aum_lakh_crore,
    ROUND(MAX(aum_crore), 0)            AS aum_crore,
    ROUND(
        100.0 * (MAX(aum_crore) - LAG(MAX(aum_crore)) OVER (
            PARTITION BY fund_house ORDER BY SUBSTR(date, 1, 4)
        )) / LAG(MAX(aum_crore)) OVER (
            PARTITION BY fund_house ORDER BY SUBSTR(date, 1, 4)
        ), 1
    )                                   AS yoy_growth_pct
FROM fact_aum
GROUP BY fund_house, year
ORDER BY fund_house, year;
