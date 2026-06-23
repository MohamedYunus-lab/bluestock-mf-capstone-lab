-- Bluestock MF Capstone - Database Schema
-- Star Schema Design for Mutual Fund Analytics Platform
-- Created: Day 2

-- =============================================================================
-- DIMENSION TABLE: Fund Master
-- =============================================================================
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code TEXT PRIMARY KEY,
    fund_house TEXT,
    scheme_name TEXT,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    launch_date DATE,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount INTEGER,
    min_lumpsum_amount INTEGER,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- =============================================================================
-- DIMENSION TABLE: Date
-- =============================================================================
CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    is_weekday INTEGER
);

-- =============================================================================
-- FACT TABLE: NAV History
-- =============================================================================
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT,
    date DATE,
    nav REAL,
    daily_return_pct REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX IF NOT EXISTS idx_fact_nav_code ON fact_nav(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_nav_date ON fact_nav(date);

-- =============================================================================
-- FACT TABLE: Transactions
-- =============================================================================
CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT,
    amfi_code TEXT,
    transaction_date DATE,
    transaction_type TEXT,
    amount_inr REAL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX IF NOT EXISTS idx_fact_transactions_code ON fact_transactions(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_transactions_date ON fact_transactions(transaction_date);

-- =============================================================================
-- FACT TABLE: Scheme Performance
-- =============================================================================
CREATE TABLE IF NOT EXISTS fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT,
    as_of_date DATE,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX IF NOT EXISTS idx_fact_performance_code ON fact_performance(amfi_code);

-- =============================================================================
-- FACT TABLE: Portfolio Holdings
-- =============================================================================
CREATE TABLE IF NOT EXISTS fact_portfolio (
    holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT,
    stock_symbol TEXT,
    stock_name TEXT,
    sector TEXT,
    weight_pct REAL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date DATE,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE INDEX IF NOT EXISTS idx_fact_portfolio_code ON fact_portfolio(amfi_code);

-- =============================================================================
-- FACT TABLE: AUM by Fund House
-- =============================================================================
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house TEXT,
    date DATE,
    aum_lakh_crore REAL,
    aum_crore REAL,
    num_schemes INTEGER
);

CREATE INDEX IF NOT EXISTS idx_fact_aum_date ON fact_aum(date);

-- =============================================================================
-- FACT TABLE: Industry SIP Inflows
-- =============================================================================
CREATE TABLE IF NOT EXISTS fact_sip_industry (
    sip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

CREATE INDEX IF NOT EXISTS idx_fact_sip_month ON fact_sip_industry(month);

-- =============================================================================
-- FACT TABLE: Category Inflows
-- =============================================================================
CREATE TABLE IF NOT EXISTS fact_category_inflows (
    inflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT,
    category TEXT,
    net_inflow_crore REAL
);

CREATE INDEX IF NOT EXISTS idx_fact_category_month ON fact_category_inflows(month);

-- =============================================================================
-- FACT TABLE: Industry Folio Count
-- =============================================================================
CREATE TABLE IF NOT EXISTS fact_folio_count (
    folio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT,
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

-- =============================================================================
-- FACT TABLE: Benchmark Indices
-- =============================================================================
CREATE TABLE IF NOT EXISTS fact_benchmark (
    benchmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    index_name TEXT,
    close_value REAL
);

CREATE INDEX IF NOT EXISTS idx_fact_benchmark_date ON fact_benchmark(date);
CREATE INDEX IF NOT EXISTS idx_fact_benchmark_name ON fact_benchmark(index_name);

