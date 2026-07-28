"""
Dashboard Database Utilities - Data Loading with Caching
Day 22: Cached data loader functions for dashboard screens
"""

import sqlite3
import pandas as pd
import logging
from functools import lru_cache
from typing import List, Dict, Optional, Tuple
import os

logger = logging.getLogger(__name__)

DB_PATH = os.getenv('DB_PATH', 'c:/bluestock-mf-capstone/n100/db/nifty100.db')


@lru_cache(maxsize=1)
def get_db_connection():
    """Get cached database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_all_companies() -> pd.DataFrame:
    """Load all companies with sector info"""
    query = """
    SELECT c.company_id, c.company_name, c.sector_id, s.sector_name, 
           c.market_cap_inr, c.bse_code, c.nse_code, c.isin
    FROM companies c
    LEFT JOIN sectors s ON c.sector_id = s.sector_id
    ORDER BY c.company_name
    """
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn)
    return df


def load_company_by_id(company_id: str) -> Optional[Dict]:
    """Load single company details"""
    query = """
    SELECT c.company_id, c.company_name, c.sector_id, s.sector_name, 
           c.market_cap_inr, c.bse_code, c.nse_code, c.isin
    FROM companies c
    LEFT JOIN sectors s ON c.sector_id = s.sector_id
    WHERE c.company_id = ?
    """
    conn = get_db_connection()
    cursor = conn.execute(query, (company_id,))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None


def load_sectors() -> pd.DataFrame:
    """Load all sectors"""
    query = "SELECT sector_id, sector_name FROM sectors ORDER BY sector_name"
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn)
    return df


def load_company_ratios(company_id: str, years: int = 10) -> pd.DataFrame:
    """Load company financial ratios for last N years"""
    query = """
    SELECT fr.year, fr.npm, fr.opm, fr.roe, fr.roa, fr.roce, fr.debt_to_equity,
           fr.icr, fr.asset_turnover, fr.fcf, fr.ocf_to_sales, fr.capex_intensity,
           fr.pe_ratio, fr.pb_ratio, fr.dividend_yield, fr.ev_ebitda
    FROM financial_ratios fr
    WHERE fr.company_id = ?
    ORDER BY fr.year DESC
    LIMIT ?
    """
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=(company_id, years))
    return df.sort_values('year')


def load_company_profitandloss(company_id: str, years: int = 10) -> pd.DataFrame:
    """Load P&L data for company"""
    query = """
    SELECT year, revenue_cr, net_profit_cr, operating_profit_cr, eps
    FROM profitandloss
    WHERE company_id = ?
    ORDER BY year DESC
    LIMIT ?
    """
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=(company_id, years))
    return df.sort_values('year')


def load_company_balancesheet(company_id: str, year: int) -> Optional[Dict]:
    """Load balance sheet for specific year"""
    query = """
    SELECT year, total_assets_cr, total_liabilities_cr, equity_cr,
           cash_and_equivalents_cr, inventory_cr, receivables_cr
    FROM balancesheet
    WHERE company_id = ? AND year = ?
    """
    conn = get_db_connection()
    cursor = conn.execute(query, (company_id, year))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None


def load_peer_group(company_id: str) -> pd.DataFrame:
    """Load peer companies for given company"""
    query = """
    SELECT DISTINCT c.company_id, c.company_name, c.sector_id, s.sector_name
    FROM peer_groups pg
    JOIN companies c ON pg.peer_company_id = c.company_id
    LEFT JOIN sectors s ON c.sector_id = s.sector_id
    WHERE pg.company_id = ?
    ORDER BY c.company_name
    """
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=(company_id,))
    return df


def load_sector_companies(sector_id: str) -> pd.DataFrame:
    """Load all companies in a sector"""
    query = """
    SELECT company_id, company_name, market_cap_inr
    FROM companies
    WHERE sector_id = ?
    ORDER BY market_cap_inr DESC
    """
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=(sector_id,))
    return df


def load_sector_medians(sector_id: str, year: int) -> Optional[Dict]:
    """Load median ratios for sector in given year"""
    query = """
    SELECT 
        AVG(fr.roe) as avg_roe,
        AVG(fr.roce) as avg_roce,
        AVG(fr.opm) as avg_opm,
        AVG(fr.npm) as avg_npm,
        AVG(fr.pe_ratio) as avg_pe,
        AVG(fr.pb_ratio) as avg_pb,
        AVG(fr.debt_to_equity) as avg_de,
        AVG(fr.dividend_yield) as avg_dividend_yield
    FROM financial_ratios fr
    JOIN companies c ON fr.company_id = c.company_id
    WHERE c.sector_id = ? AND fr.year = ?
    """
    conn = get_db_connection()
    cursor = conn.execute(query, (sector_id, year))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None


def load_latest_stock_price(company_id: str) -> Optional[Dict]:
    """Load latest stock price"""
    query = """
    SELECT company_id, date, close_price, volume
    FROM stock_prices
    WHERE company_id = ?
    ORDER BY date DESC
    LIMIT 1
    """
    conn = get_db_connection()
    cursor = conn.execute(query, (company_id,))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None


def load_prosandcons(company_id: str, year: int) -> Optional[Dict]:
    """Load pros and cons for company-year"""
    query = """
    SELECT pros, cons FROM prosandcons
    WHERE company_id = ? AND year = ?
    """
    conn = get_db_connection()
    cursor = conn.execute(query, (company_id, year))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None


def load_annual_report_links(company_id: str) -> pd.DataFrame:
    """Load annual report document links"""
    query = """
    SELECT year, doc_url, filing_date
    FROM documents
    WHERE company_id = ? AND doc_type = 'Annual_Report'
    ORDER BY year DESC
    """
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=(company_id,))
    return df


def load_company_cashflow(company_id: str, years: int = 10) -> pd.DataFrame:
    """Load cashflow data for company"""
    query = """
    SELECT year, operating_cf_cr, investing_cf_cr, financing_cf_cr, 
           net_cash_change_cr, free_cash_flow_cr
    FROM cashflow
    WHERE company_id = ?
    ORDER BY year DESC
    LIMIT ?
    """
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=(company_id, years))
    return df.sort_values('year')


def get_kpi_summary(year: int = None) -> Dict:
    """Get KPI summary for home screen (latest year if not specified)"""
    if year is None:
        # Get latest year
        query_year = "SELECT MAX(year) as max_year FROM financial_ratios"
        conn = get_db_connection()
        cursor = conn.execute(query_year)
        result = cursor.fetchone()
        year = result['max_year'] if result else 2023
    
    query = """
    SELECT 
        COUNT(DISTINCT c.company_id) as total_companies,
        AVG(fr.roe) as avg_roe,
        AVG(fr.pe_ratio) as median_pe,
        AVG(fr.debt_to_equity) as median_de,
        AVG((SELECT AVG(revenue_cr) FROM profitandloss WHERE year = ?)) as avg_revenue,
        COUNT(DISTINCT CASE WHEN fr.debt_to_equity = 0 THEN c.company_id END) as debt_free_count
    FROM companies c
    LEFT JOIN financial_ratios fr ON c.company_id = fr.company_id AND fr.year = ?
    """
    conn = get_db_connection()
    cursor = conn.execute(query, (year, year))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return {}


def get_sector_distribution(year: int = None) -> pd.DataFrame:
    """Get company count and avg metrics by sector"""
    if year is None:
        query_year = "SELECT MAX(year) as max_year FROM financial_ratios"
        conn = get_db_connection()
        cursor = conn.execute(query_year)
        result = cursor.fetchone()
        year = result['max_year'] if result else 2023
    
    query = """
    SELECT 
        s.sector_name,
        COUNT(DISTINCT c.company_id) as count,
        AVG(fr.roe) as avg_roe,
        AVG(fr.pe_ratio) as avg_pe
    FROM sectors s
    LEFT JOIN companies c ON s.sector_id = c.sector_id
    LEFT JOIN financial_ratios fr ON c.company_id = fr.company_id AND fr.year = ?
    GROUP BY s.sector_id, s.sector_name
    ORDER BY count DESC
    """
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=(year,))
    return df


def get_top_companies_by_metric(metric: str = 'roe', year: int = None, limit: int = 5) -> pd.DataFrame:
    """Get top N companies by specified metric"""
    if year is None:
        query_year = "SELECT MAX(year) as max_year FROM financial_ratios"
        conn = get_db_connection()
        cursor = conn.execute(query_year)
        result = cursor.fetchone()
        year = result['max_year'] if result else 2023
    
    valid_metrics = ['roe', 'roce', 'opm', 'npm', 'pe_ratio', 'dividend_yield']
    if metric not in valid_metrics:
        metric = 'roe'
    
    query = f"""
    SELECT 
        c.company_id,
        c.company_name,
        s.sector_name,
        fr.{metric} as metric_value
    FROM companies c
    LEFT JOIN sectors s ON c.sector_id = s.sector_id
    LEFT JOIN financial_ratios fr ON c.company_id = fr.company_id AND fr.year = ?
    WHERE fr.{metric} IS NOT NULL
    ORDER BY fr.{metric} DESC
    LIMIT ?
    """
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=(year, limit))
    return df


def search_companies(search_term: str) -> pd.DataFrame:
    """Search companies by name or ticker"""
    query = """
    SELECT company_id, company_name, sector_id, bse_code, nse_code
    FROM companies
    WHERE company_name LIKE ? OR bse_code LIKE ? OR nse_code LIKE ?
    ORDER BY company_name
    """
    conn = get_db_connection()
    search_pattern = f"%{search_term}%"
    df = pd.read_sql_query(query, conn, params=(search_pattern, search_pattern, search_pattern))
    return df


def get_available_years() -> List[int]:
    """Get list of available years in database"""
    query = "SELECT DISTINCT year FROM financial_ratios ORDER BY year DESC"
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn)
    return sorted(df['year'].tolist(), reverse=True) if not df.empty else []
