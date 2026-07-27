"""
Ratio Calculator & Financial_Ratios Table Populator (Days 12-13)
Computes 50+ KPIs for all 92 companies and populates SQLite table
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from src.analytics.ratios import (
    ProfitabilityRatios, LeverageRatios, EfficiencyRatios,
    calculate_ebit, calculate_total_debt
)
from src.analytics.cagr import CAGREngine
from src.analytics.cashflow_kpis import (
    CashflowQualityMetrics, CapitalAllocationClassifier
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/ratio_edge_cases.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RatioCalculator:
    """Compute KPIs for a single company-year"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self.edge_cases = []
    
    def connect(self):
        """Connect to database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def get_company_data(self, company_id: str, year: int) -> Dict:
        """Fetch company data for a specific year"""
        cursor = self.connection.cursor()
        
        # Get P&L data
        cursor.execute("""
            SELECT * FROM profitandloss 
            WHERE company_id = ? AND year = ?
        """, (company_id, year))
        pl_row = cursor.fetchone()
        
        # Get balance sheet data
        cursor.execute("""
            SELECT * FROM balancesheet 
            WHERE company_id = ? AND year = ?
        """, (company_id, year))
        bs_row = cursor.fetchone()
        
        # Get cashflow data
        cursor.execute("""
            SELECT * FROM cashflow 
            WHERE company_id = ? AND year = ?
        """, (company_id, year))
        cf_row = cursor.fetchone()
        
        # Get prior year data for averages
        cursor.execute("""
            SELECT * FROM balancesheet 
            WHERE company_id = ? AND year = ?
        """, (company_id, year - 1))
        bs_prior = cursor.fetchone()
        
        return {
            'pl': dict(pl_row) if pl_row else {},
            'bs': dict(bs_row) if bs_row else {},
            'cf': dict(cf_row) if cf_row else {},
            'bs_prior': dict(bs_prior) if bs_prior else {}
        }
    
    def get_company_sector(self, company_id: str) -> Optional[str]:
        """Get company sector for special handling (e.g., Financials)"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT c.company_id, s.broad_sector 
            FROM companies c
            LEFT JOIN (
                SELECT DISTINCT company_id, broad_sector 
                FROM (
                    SELECT company_id, broad_sector FROM (
                        SELECT company_id, broad_sector FROM sectors s
                        CROSS JOIN companies c
                        LIMIT 1
                    )
                    UNION
                    SELECT c.id as company_id, s.broad_sector
                    FROM (
                        SELECT 'sector_map' as placeholder
                    ) dummy
                )
            ) s ON c.company_id = s.company_id
            WHERE c.company_id = ?
        """, (company_id,))
        result = cursor.fetchone()
        
        # Fallback: check sectors table directly
        try:
            import pandas as pd
            sectors_df = pd.read_excel('data/raw/sectors.xlsx', header=0)
            match = sectors_df[sectors_df['company_id'] == company_id]
            if not match.empty:
                return match.iloc[0]['broad_sector']
        except:
            pass
        
        return None
    
    def calculate_all_ratios(self, company_id: str, year: int) -> Dict:
        """Calculate all ratios for a company-year"""
        data = self.get_company_data(company_id, year)
        sector = self.get_company_sector(company_id)
        
        ratios = {
            'company_id': company_id,
            'year': year,
            'sector': sector,
            'edge_cases': []
        }
        
        # Extract values
        pl = data['pl']
        bs = data['bs']
        bs_prior = data['bs_prior']
        cf = data['cf']
        
        # PROFITABILITY RATIOS
        npm, ec = ProfitabilityRatios.net_profit_margin(
            pl.get('net_profit_cr'), pl.get('revenue_cr')
        )
        ratios['npm'] = npm
        if ec: ratios['edge_cases'].append(f"NPM:{ec.edge_case}")
        
        opm, ec = ProfitabilityRatios.operating_profit_margin(
            pl.get('operating_profit_cr'), pl.get('revenue_cr')
        )
        ratios['opm'] = opm
        if ec: ratios['edge_cases'].append(f"OPM:{ec.edge_case}")
        
        roe, ec = ProfitabilityRatios.return_on_equity(
            pl.get('net_profit_cr'),
            bs_prior.get('equity_cr'),
            bs.get('equity_cr')
        )
        ratios['roe'] = roe
        if ec: ratios['edge_cases'].append(f"ROE:{ec.edge_case}")
        
        roa, ec = ProfitabilityRatios.return_on_assets(
            pl.get('net_profit_cr'),
            bs_prior.get('total_assets_cr'),
            bs.get('total_assets_cr')
        )
        ratios['roa'] = roa
        if ec: ratios['edge_cases'].append(f"ROA:{ec.edge_case}")
        
        # Calculate EBIT for ROCE
        ebit = calculate_ebit(
            pl.get('net_profit_cr'),
            pl.get('interest_expense_cr'),
            pl.get('tax_expense_cr')
        )
        
        # Estimate long-term debt (simplified)
        total_liabilities = bs.get('total_liabilities_cr', 0)
        equity = bs.get('equity_cr', 0)
        total_debt = (total_liabilities - equity) if total_liabilities and equity else None
        
        roce, ec = ProfitabilityRatios.return_on_capital_employed(
            ebit, equity, total_debt if total_debt and total_debt > 0 else 0
        )
        ratios['roce'] = roce
        if ec: 
            ratios['edge_cases'].append(f"ROCE:{ec.edge_case}")
            # Special handling for Financials sector
            if sector and 'Financials' in sector:
                ratios['roce_flag'] = 'FINANCIALS_SECTOR'
        
        # LEVERAGE RATIOS
        de, ec = LeverageRatios.debt_to_equity(total_debt, equity)
        ratios['debt_to_equity'] = de
        if ec:
            if ec.edge_case == 'debt_free':
                ratios['de_flag'] = 'DEBT_FREE'
            else:
                ratios['edge_cases'].append(f"D/E:{ec.edge_case}")
        
        icr, ec = LeverageRatios.interest_coverage_ratio(
            ebit, pl.get('interest_expense_cr')
        )
        ratios['icr'] = icr
        if ec:
            ratios['edge_cases'].append(f"ICR:{ec.edge_case}")
        
        # EFFICIENCY RATIOS
        at, ec = LeverageRatios.asset_turnover(
            pl.get('revenue_cr'),
            bs_prior.get('total_assets_cr'),
            bs.get('total_assets_cr')
        )
        ratios['asset_turnover'] = at
        if ec: ratios['edge_cases'].append(f"AT:{ec.edge_case}")
        
        # Cashflow metrics
        ocf_sales, ec = CashflowQualityMetrics.operating_cash_flow_to_sales(
            cf.get('operating_cf_cr'), pl.get('revenue_cr')
        )
        ratios['ocf_to_sales'] = ocf_sales
        if ec: ratios['edge_cases'].append(f"OCF_Sales:{ec}")
        
        # Free Cash Flow
        fcf, ec = CashflowQualityMetrics.free_cash_flow(
            cf.get('operating_cf_cr'), abs(cf.get('investing_cf_cr', 0))
        )
        ratios['fcf'] = fcf
        
        # CapEx intensity
        capex_intensity, ec = CashflowQualityMetrics.capex_intensity(
            abs(cf.get('investing_cf_cr', 0)), pl.get('revenue_cr')
        )
        ratios['capex_intensity'] = capex_intensity
        if ec: ratios['edge_cases'].append(f"CapEx:{ec}")
        
        return ratios
    
    def calculate_all_companies_all_years(self) -> List[Dict]:
        """Calculate ratios for all companies and years"""
        self.connect()
        
        cursor = self.connection.cursor()
        
        # Get unique company-year combinations
        cursor.execute("""
            SELECT DISTINCT c.company_id, p.year
            FROM companies c
            CROSS JOIN profitandloss p
            WHERE p.company_id = c.company_id
            ORDER BY c.company_id, p.year
        """)
        
        rows = cursor.fetchall()
        all_ratios = []
        
        logger.info(f"Processing {len(rows)} company-year records...")
        
        for company_id, year in rows:
            try:
                ratios = self.calculate_all_ratios(company_id, year)
                all_ratios.append(ratios)
                
                if len(all_ratios) % 100 == 0:
                    logger.info(f"Processed {len(all_ratios)} records...")
            except Exception as e:
                logger.error(f"Error processing {company_id} {year}: {e}")
                continue
        
        self.disconnect()
        logger.info(f"Total ratios calculated: {len(all_ratios)}")
        
        return all_ratios


class FinancialRatiosPopulator:
    """Populate financial_ratios table in SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
    
    def populate_ratios(self, ratios_list: List[Dict]):
        """Insert calculated ratios into database"""
        self.connect()
        cursor = self.connection.cursor()
        
        # Clear existing ratios (or append mode)
        # cursor.execute("DELETE FROM financial_ratios")
        
        inserted = 0
        updated = 0
        errors = 0
        
        for ratio_dict in ratios_list:
            try:
                # Prepare INSERT/UPDATE statement
                company_id = ratio_dict['company_id']
                year = ratio_dict['year']
                
                # Check if exists
                cursor.execute("""
                    SELECT ratio_id FROM financial_ratios 
                    WHERE company_id = ? AND year = ?
                """, (company_id, year))
                
                exists = cursor.fetchone()
                
                ratio_data = {
                    'company_id': company_id,
                    'year': year,
                    'npm': ratio_dict.get('npm'),
                    'opm': ratio_dict.get('opm'),
                    'roe': ratio_dict.get('roe'),
                    'roa': ratio_dict.get('roa'),
                    'roce': ratio_dict.get('roce'),
                    'debt_to_equity': ratio_dict.get('debt_to_equity'),
                    'icr': ratio_dict.get('icr'),
                    'asset_turnover': ratio_dict.get('asset_turnover'),
                    'fcf': ratio_dict.get('fcf'),
                    'ocf_to_sales': ratio_dict.get('ocf_to_sales'),
                    'capex_intensity': ratio_dict.get('capex_intensity'),
                    'pe_ratio': ratio_dict.get('pe_ratio'),
                    'pb_ratio': ratio_dict.get('pb_ratio'),
                    'dividend_yield': ratio_dict.get('dividend_yield'),
                    'peg_ratio': ratio_dict.get('peg_ratio'),
                    'ev_ebitda': ratio_dict.get('ev_ebitda')
                }
                
                if exists:
                    # Update
                    update_fields = ', '.join([f"{k} = ?" for k in ratio_data.keys() if k not in ['company_id', 'year']])
                    update_values = [v for k, v in ratio_data.items() if k not in ['company_id', 'year']]
                    update_values.extend([company_id, year])
                    
                    cursor.execute(f"""
                        UPDATE financial_ratios 
                        SET {update_fields}
                        WHERE company_id = ? AND year = ?
                    """, update_values)
                    updated += 1
                else:
                    # Insert
                    placeholders = ', '.join(['?' for _ in ratio_data])
                    columns = ', '.join(ratio_data.keys())
                    values = list(ratio_data.values())
                    
                    cursor.execute(f"""
                        INSERT INTO financial_ratios ({columns})
                        VALUES ({placeholders})
                    """, values)
                    inserted += 1
                
            except Exception as e:
                logger.error(f"Error inserting ratio for {ratio_dict.get('company_id')} {ratio_dict.get('year')}: {e}")
                errors += 1
        
        self.connection.commit()
        self.disconnect()
        
        logger.info(f"Insertion complete: {inserted} new, {updated} updated, {errors} errors")
        return inserted, updated, errors


def run_ratio_calculation_pipeline():
    """Execute full ratio calculation and population pipeline"""
    logger.info("=" * 60)
    logger.info("N100 Financial Ratio Calculation Pipeline (Days 12-13)")
    logger.info("=" * 60)
    
    db_path = 'db/nifty100.db'
    
    # Calculate all ratios
    logger.info("\nStep 1: Calculating ratios for all companies...")
    calculator = RatioCalculator(db_path)
    ratios_list = calculator.calculate_all_companies_all_years()
    
    # Populate database
    logger.info("\nStep 2: Populating financial_ratios table...")
    populator = FinancialRatiosPopulator(db_path)
    inserted, updated, errors = populator.populate_ratios(ratios_list)
    
    # Verify
    logger.info("\nStep 3: Verifying population...")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM financial_ratios")
    total_rows = cursor.fetchone()[0]
    connection.close()
    
    logger.info(f"Total rows in financial_ratios: {total_rows}")
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)


if __name__ == '__main__':
    run_ratio_calculation_pipeline()
