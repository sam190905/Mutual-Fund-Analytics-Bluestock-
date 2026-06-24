-- ============================================================
-- schema.sql
-- Bluestock MF Analytics — SQLite Star Schema
-- Day 2: Database Design
-- ============================================================

-- DIMENSION: Fund master
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code           INTEGER     PRIMARY KEY,
    fund_house          TEXT        NOT NULL,
    scheme_name         TEXT        NOT NULL,
    category            TEXT,
    sub_category        TEXT,
    plan                TEXT,
    launch_date         TEXT,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      INTEGER,
    min_lumpsum_amount  INTEGER,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);

-- DIMENSION: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_id     INTEGER     PRIMARY KEY,
    date        TEXT        NOT NULL UNIQUE,
    year        INTEGER,
    month       INTEGER,
    quarter     INTEGER,
    month_name  TEXT,
    is_weekday  INTEGER
);

-- FACT: Daily NAV
CREATE TABLE IF NOT EXISTS fact_nav (
    id                  INTEGER     PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER     NOT NULL,
    date                TEXT        NOT NULL,
    nav                 REAL        NOT NULL,
    daily_return_pct    REAL,
    UNIQUE (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- FACT: Investor transactions (no tx_id in source — use autoincrement)
CREATE TABLE IF NOT EXISTS fact_transactions (
    id                  INTEGER     PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT        NOT NULL,
    amfi_code           INTEGER     NOT NULL,
    transaction_date    TEXT        NOT NULL,
    transaction_type    TEXT        NOT NULL CHECK (transaction_type IN ('SIP','Lumpsum','Redemption')),
    amount_inr          INTEGER     NOT NULL,
    state               TEXT,
    city                TEXT,
    city_tier           TEXT,
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- FACT: Scheme performance metrics
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code           INTEGER     PRIMARY KEY,
    scheme_name         TEXT,
    fund_house          TEXT,
    category            TEXT,
    plan                TEXT,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           INTEGER,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER,
    risk_grade          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- FACT: AUM by fund house per quarter
CREATE TABLE IF NOT EXISTS fact_aum (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,
    date            TEXT        NOT NULL,
    fund_house      TEXT        NOT NULL,
    aum_lakh_crore  REAL,
    aum_crore       INTEGER,
    num_schemes     INTEGER,
    UNIQUE (fund_house, date)
);

-- FACT: Monthly SIP industry inflows
CREATE TABLE IF NOT EXISTS fact_sip_industry (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    month                       TEXT    NOT NULL UNIQUE,
    sip_inflow_crore            INTEGER,
    active_sip_accounts_crore   REAL,
    new_sip_accounts_lakh       REAL,
    sip_aum_lakh_crore          REAL,
    yoy_growth_pct              REAL
);

-- FACT: Category net inflows
CREATE TABLE IF NOT EXISTS fact_category_inflows (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    month               TEXT    NOT NULL,
    category            TEXT    NOT NULL,
    net_inflow_crore    REAL,
    UNIQUE (month, category)
);

-- FACT: Industry folio count
CREATE TABLE IF NOT EXISTS fact_folio_count (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    month                   TEXT    NOT NULL UNIQUE,
    total_folios_crore      REAL,
    equity_folios_crore     REAL,
    debt_folios_crore       REAL,
    hybrid_folios_crore     REAL,
    others_folios_crore     REAL
);

-- FACT: Portfolio holdings
CREATE TABLE IF NOT EXISTS fact_portfolio (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL,
    stock_symbol        TEXT,
    stock_name          TEXT,
    sector              TEXT,
    weight_pct          REAL,
    market_value_cr     REAL,
    current_price_inr   REAL,
    portfolio_date      TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- FACT: Benchmark indices
CREATE TABLE IF NOT EXISTS fact_benchmark (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT    NOT NULL,
    index_name  TEXT    NOT NULL,
    close_value REAL,
    UNIQUE (date, index_name)
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_nav_amfi_date     ON fact_nav(amfi_code, date);
CREATE INDEX IF NOT EXISTS idx_nav_date          ON fact_nav(date);
CREATE INDEX IF NOT EXISTS idx_tx_amfi           ON fact_transactions(amfi_code);
CREATE INDEX IF NOT EXISTS idx_tx_date           ON fact_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_tx_state          ON fact_transactions(state);
CREATE INDEX IF NOT EXISTS idx_portfolio_amfi    ON fact_portfolio(amfi_code);
CREATE INDEX IF NOT EXISTS idx_benchmark_date    ON fact_benchmark(date, index_name);
