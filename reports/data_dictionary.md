Bluestock MF Capstone Project – Data Dictionary

01. fund_master_clean.csv
Description: Master list of mutual fund schemes with metadata.
Columns: amfi_code, fund_house, scheme_name, category, sub_category, plan, launch_date, benchmark, expense_ratio_pct, exit_load_pct, min_sip_amount, min_lumpsum_amount, fund_manager, risk_category, sebi_category_code
Cleaning Steps: Standardized column names, converted launch_date to date format, filled missing categories.

02. nav_history_clean.csv
Description: Daily Net Asset Value (NAV) history for schemes.
Columns: amfi_code, date, nav
Cleaning Steps: Converted date to date format, standardized column names.

03. aum_by_fund_house_clean.csv
Description: Assets Under Management (AUM) by fund house.
Columns: date, fund_house, aum_lakh_crore, aum_crore, num_schemes
Cleaning Steps: Converted date to date format, standardized column names.

04. monthly_sip_inflows_clean.csv
Description: Monthly inflows from Systematic Investment Plans (SIP).
Columns: month, sip_inflow_crore, active_sip_accounts_crore, new_sip_accounts_lakh, sip_aum_lakh_crore, yoy_growth_pct
Cleaning Steps: Converted month to date format, standardized column names, filled missing growth values.

05. category_inflows_clean.csv
Description: Inflows by mutual fund category.
Columns: month, category, net_inflow_crore
Cleaning Steps: Converted month to date format, standardized category names.

06. industry_folio_count_clean.csv
Description: Folio counts across industries.
Columns: month, total_folios_crore, equity_folios_crore, debt_folios_crore, hybrid_folios_crore, others_folios_crore
Cleaning Steps: Converted month to date format, ensured numeric columns are floats.

07. scheme_performance_clean.csv
Description: Performance metrics of schemes.
Columns: amfi_code, scheme_name, fund_house, category, plan, return_1yr_pct, return_3yr_pct, return_5yr_pct, benchmark_3yr_pct, alpha, beta, sharpe_ratio, sortino_ratio, std_dev_ann_pct, max_drawdown_pct, aum_crore, expense_ratio_pct, morningstar_rating, risk_grade
Cleaning Steps: Converted returns to numeric, standardized column names.

08. investor_transactions_clean.csv
Description: Investor transaction records.
Columns: investor_id, transaction_date, amfi_code, transaction_type, amount_inr, state, city, city_tier, age_group, gender, annual_income_lakh, payment_mode, kyc_status
Cleaning Steps: Converted transaction_date to date format, standardized column names.

09. portfolio_holdings_clean.csv
Description: Portfolio holdings of schemes.
Columns: amfi_code, stock_symbol, stock_name, sector, weight_pct, market_value_cr, current_price_inr, portfolio_date
Cleaning Steps: Converted portfolio_date to date format, standardized column names.

10. benchmark_indices_clean.csv
Description: Benchmark index values for comparison.
Columns: date, index_name, close_value
Cleaning Steps: Converted date to date format, standardized column names.