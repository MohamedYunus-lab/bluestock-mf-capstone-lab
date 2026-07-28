-- Bluestock MF Capstone - Analytical SQL Queries
-- Day 2: Database Validation & Analysis Queries

-- =============================================================================
-- QUERY 1: Top 5 Funds by AUM (Task #6 requirement)
-- =============================================================================
SELECT 
    f.scheme_name,
    f.fund_house,
    f.category,
    p.aum_crore,
    ROUND(p.aum_crore / 100, 2) as aum_lakh_crore
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.aum_crore IS NOT NULL
ORDER BY p.aum_crore DESC
LIMIT 5;

-- =============================================================================
-- QUERY 2: Average NAV per Month (Task #6 requirement)
-- =============================================================================
SELECT 
    strftime('%Y-%m', date) as month,
    amfi_code,
    ROUND(AVG(nav), 2) as avg_nav,
    COUNT(*) as trading_days
FROM fact_nav
GROUP BY strftime('%Y-%m', date), amfi_code
ORDER BY month DESC, avg_nav DESC
LIMIT 20;

-- =============================================================================
-- QUERY 3: SIP Inflow YoY Growth (Task #6 requirement)
-- =============================================================================
SELECT 
    month,
    sip_inflow_crore,
    active_sip_accounts_crore,
    yoy_growth_pct,
    CASE 
        WHEN yoy_growth_pct > 20 THEN 'High Growth'
        WHEN yoy_growth_pct > 10 THEN 'Moderate Growth'
        ELSE 'Slow Growth'
    END as growth_category
FROM fact_sip_industry
ORDER BY month DESC
LIMIT 12;

-- =============================================================================
-- QUERY 4: Transactions by State (Task #6 requirement)
-- =============================================================================
SELECT 
    state,
    COUNT(*) as total_transactions,
    SUM(amount_inr) as total_amount,
    ROUND(AVG(amount_inr), 2) as avg_transaction_amount,
    COUNT(DISTINCT investor_id) as unique_investors
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC;

-- =============================================================================
-- QUERY 5: Funds with Expense Ratio < 1% (Task #6 requirement)
-- =============================================================================
SELECT 
    amfi_code,
    scheme_name,
    fund_house,
    category,
    expense_ratio_pct,
    plan
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- =============================================================================
-- QUERY 6: Best Performing Funds by Sharpe Ratio
-- =============================================================================
SELECT 
    f.scheme_name,
    f.fund_house,
    f.category,
    p.sharpe_ratio,
    p.return_3yr_pct,
    p.alpha,
    p.max_drawdown_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.sharpe_ratio IS NOT NULL
ORDER BY p.sharpe_ratio DESC
LIMIT 10;

-- =============================================================================
-- QUERY 7: Fund House AUM Ranking
-- =============================================================================
SELECT 
    fund_house,
    SUM(aum_crore) as total_aum_crore,
    ROUND(SUM(aum_crore) / 100000, 2) as total_aum_lakh_crore,
    COUNT(*) as num_schemes,
    ROUND(AVG(aum_crore), 2) as avg_aum_per_scheme
FROM fact_aum
WHERE date = (SELECT MAX(date) FROM fact_aum)
GROUP BY fund_house
ORDER BY total_aum_crore DESC;

-- =============================================================================
-- QUERY 8: Category-wise Net Inflows (Last 6 Months)
-- =============================================================================
SELECT 
    category,
    COUNT(*) as num_months,
    SUM(net_inflow_crore) as total_inflow,
    ROUND(AVG(net_inflow_crore), 2) as avg_monthly_inflow
FROM fact_category_inflows
WHERE month >= date('now', '-6 months')
GROUP BY category
ORDER BY total_inflow DESC;

-- =============================================================================
-- QUERY 9: High-Risk High-Return Funds
-- =============================================================================
SELECT 
    f.scheme_name,
    f.fund_house,
    f.risk_category,
    p.return_3yr_pct,
    p.std_dev_ann_pct,
    p.max_drawdown_pct,
    p.sharpe_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE f.risk_category IN ('High', 'Very High')
    AND p.return_3yr_pct > 15
ORDER BY p.return_3yr_pct DESC
LIMIT 15;

-- =============================================================================
-- QUERY 10: Investor Demographics Analysis
-- =============================================================================
SELECT 
    age_group,
    gender,
    COUNT(*) as transaction_count,
    SUM(amount_inr) as total_invested,
    ROUND(AVG(amount_inr), 2) as avg_investment,
    COUNT(DISTINCT investor_id) as unique_investors
FROM fact_transactions
WHERE transaction_type IN ('SIP', 'Lumpsum')
GROUP BY age_group, gender
ORDER BY total_invested DESC;

-- =============================================================================
-- BONUS QUERY: Data Quality Check - Record Counts
-- =============================================================================
SELECT 'dim_fund' as table_name, COUNT(*) as record_count FROM dim_fund
UNION ALL
SELECT 'fact_nav', COUNT(*) FROM fact_nav
UNION ALL
SELECT 'fact_transactions', COUNT(*) FROM fact_transactions
UNION ALL
SELECT 'fact_performance', COUNT(*) FROM fact_performance
UNION ALL
SELECT 'fact_portfolio', COUNT(*) FROM fact_portfolio
UNION ALL
SELECT 'fact_aum', COUNT(*) FROM fact_aum
UNION ALL
SELECT 'fact_sip_industry', COUNT(*) FROM fact_sip_industry;

