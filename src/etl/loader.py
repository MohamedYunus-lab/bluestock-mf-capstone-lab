"""
Excel Data Loader
Loads all 12 source Excel files into SQLite with normalization
"""

import pandas as pd
import sqlite3
import os
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from normaliser import normalize_year, normalize_ticker, normalize_numeric, normalize_string


class ExcelLoader:
    """Loads Excel files into SQLite database"""
    
    def __init__(self, db_path: str, data_dir: str):
        self.db_path = db_path
        self.data_dir = data_dir
        self.load_audit = []
        self.connection = None
    
    def connect(self):
        """Connect to SQLite database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute('PRAGMA foreign_keys = ON')
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def load_all_files(self) -> Dict[str, pd.DataFrame]:
        """Load all 12 Excel files with proper header handling"""
        data_dict = {}
        
        excel_configs = {
            'companies': ('companies.xlsx', 1),
            'profitandloss': ('profitandloss.xlsx', 1),
            'balancesheet': ('balancesheet.xlsx', 1),
            'cashflow': ('cashflow.xlsx', 1),
            'analysis': ('analysis.xlsx', 1),
            'documents': ('documents.xlsx', 1),
            'prosandcons': ('prosandcons.xlsx', 1),
            'sectors': ('sectors.xlsx', 0),
            'stock_prices': ('stock_prices.xlsx', 0),
            'financial_ratios': ('financial_ratios.xlsx', 0),
            'market_cap': ('market_cap.xlsx', 0),
            'peer_groups': ('peer_groups.xlsx', 0),
        }
        
        for table_name, (filename, header_row) in excel_configs.items():
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                try:
                    df = pd.read_excel(filepath, header=header_row)
                    if header_row > 0:
                        df = df.iloc[header_row:]
                        df = df.reset_index(drop=True)
                    data_dict[table_name] = df
                    print(f"Loaded {table_name}: {len(df)} rows")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        return data_dict
    
    def normalize_row(self, row, mapping: Dict[str, callable]) -> Dict:
        """Normalize a row using column mapping"""
        result = {}
        for target_col, (source_col, func) in mapping.items():
            value = row.get(source_col)
            if pd.notna(value):
                result[target_col] = func(value) if func else value
            else:
                result[target_col] = None
        return result
    
    def normalize_companies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize companies table"""
        df_clean = df.copy()
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        result_rows = []
        for idx, row in df_clean.iterrows():
            company_id = normalize_string(row.get('id'))
            company_name = normalize_string(row.get('company_name'))
            
            if company_id and company_name:
                result_rows.append({
                    'company_id': company_id,
                    'company_name': company_name,
                    'sector_id': None,
                    'isin': None,
                    'bse_code': None,
                    'nse_code': None,
                    'market_cap_inr': normalize_numeric(row.get('book_value')) if pd.notna(row.get('book_value')) else None
                })
        
        return pd.DataFrame(result_rows) if result_rows else pd.DataFrame()
    
    def normalize_profitandloss(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize profitandloss table"""
        df_clean = df.copy()
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        result_rows = []
        for idx, row in df_clean.iterrows():
            company_id = normalize_string(row.get('company_id'))
            year = normalize_year(row.get('year'))
            
            if company_id and year:
                result_rows.append({
                    'company_id': company_id,
                    'year': year,
                    'revenue_cr': normalize_numeric(row.get('sales')) if pd.notna(row.get('sales')) else None,
                    'cost_of_goods_sold_cr': normalize_numeric(row.get('expenses')) if pd.notna(row.get('expenses')) else None,
                    'gross_profit_cr': None,
                    'operating_profit_cr': normalize_numeric(row.get('operating_profit')) if pd.notna(row.get('operating_profit')) else None,
                    'depreciation_cr': normalize_numeric(row.get('depreciation')) if pd.notna(row.get('depreciation')) else None,
                    'interest_expense_cr': normalize_numeric(row.get('interest')) if pd.notna(row.get('interest')) else None,
                    'tax_expense_cr': None,
                    'net_profit_cr': normalize_numeric(row.get('net_profit')) if pd.notna(row.get('net_profit')) else None,
                    'eps': normalize_numeric(row.get('eps')) if pd.notna(row.get('eps')) else None,
                    'opm': normalize_numeric(row.get('opm_percentage')) if pd.notna(row.get('opm_percentage')) else None,
                    'npm': None
                })
        
        return pd.DataFrame(result_rows) if result_rows else pd.DataFrame()
    
    def normalize_balancesheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize balancesheet table"""
        df_clean = df.copy()
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        result_rows = []
        for idx, row in df_clean.iterrows():
            company_id = normalize_string(row.get('company_id'))
            year = normalize_year(row.get('year'))
            
            if company_id and year:
                result_rows.append({
                    'company_id': company_id,
                    'year': year,
                    'total_assets_cr': normalize_numeric(row.get('total_assets')) if pd.notna(row.get('total_assets')) else None,
                    'current_assets_cr': None,
                    'fixed_assets_cr': normalize_numeric(row.get('fixed_assets')) if pd.notna(row.get('fixed_assets')) else None,
                    'total_liabilities_cr': normalize_numeric(row.get('total_liabilities')) if pd.notna(row.get('total_liabilities')) else None,
                    'current_liabilities_cr': None,
                    'long_term_liabilities_cr': None,
                    'equity_cr': normalize_numeric(row.get('equity_capital')) if pd.notna(row.get('equity_capital')) else None,
                    'cash_and_equivalents_cr': None,
                    'inventory_cr': None,
                    'receivables_cr': None
                })
        
        return pd.DataFrame(result_rows) if result_rows else pd.DataFrame()
    
    def normalize_cashflow(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize cashflow table"""
        df_clean = df.copy()
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        result_rows = []
        for idx, row in df_clean.iterrows():
            company_id = normalize_string(row.get('company_id'))
            year = normalize_year(row.get('year'))
            
            if company_id and year:
                result_rows.append({
                    'company_id': company_id,
                    'year': year,
                    'operating_cf_cr': normalize_numeric(row.get('operating_activity')) if pd.notna(row.get('operating_activity')) else None,
                    'investing_cf_cr': normalize_numeric(row.get('investing_activity')) if pd.notna(row.get('investing_activity')) else None,
                    'financing_cf_cr': normalize_numeric(row.get('financing_activity')) if pd.notna(row.get('financing_activity')) else None,
                    'net_cash_change_cr': normalize_numeric(row.get('net_cash_flow')) if pd.notna(row.get('net_cash_flow')) else None,
                    'free_cash_flow_cr': None
                })
        
        return pd.DataFrame(result_rows) if result_rows else pd.DataFrame()
    
    def normalize_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize analysis table"""
        df_clean = df.copy()
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        result_rows = []
        for idx, row in df_clean.iterrows():
            company_id = normalize_string(row.get('ticker') or row.get('company_id'))
            year = normalize_year(row.get('year'))
            
            if company_id and year:
                result_rows.append({
                    'company_id': company_id,
                    'year': year,
                    'roe': None,
                    'roa': None,
                    'roic': None,
                    'debt_to_equity': None,
                    'current_ratio': None,
                    'quick_ratio': None,
                    'debt_to_ebitda': None
                })
        
        return pd.DataFrame(result_rows) if result_rows else pd.DataFrame()
    
    def normalize_sectors(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize sectors table"""
        df_clean = df.copy()
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        result_rows = []
        seen_sectors = set()
        
        for idx, row in df_clean.iterrows():
            sector_name = normalize_string(row.get('broad_sector'))
            if sector_name and sector_name not in seen_sectors:
                sector_id = sector_name.upper().replace(' ', '_')
                result_rows.append({
                    'sector_id': sector_id,
                    'sector_name': sector_name
                })
                seen_sectors.add(sector_name)
        
        return pd.DataFrame(result_rows) if result_rows else pd.DataFrame()
    
    def normalize_stock_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize stock_prices table"""
        df_clean = df.copy()
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        result_rows = []
        for idx, row in df_clean.iterrows():
            ticker = normalize_string(row.get('company_id'))
            if ticker and pd.notna(row.get('date')):
                result_rows.append({
                    'company_id': ticker,
                    'date': pd.to_datetime(row.get('date')).date() if pd.notna(row.get('date')) else None,
                    'open_price': normalize_numeric(row.get('open_price')) if pd.notna(row.get('open_price')) else None,
                    'high_price': normalize_numeric(row.get('high_price')) if pd.notna(row.get('high_price')) else None,
                    'low_price': normalize_numeric(row.get('low_price')) if pd.notna(row.get('low_price')) else None,
                    'close_price': normalize_numeric(row.get('close_price')) if pd.notna(row.get('close_price')) else None,
                    'volume': normalize_numeric(row.get('volume')) if pd.notna(row.get('volume')) else None
                })
        
        return pd.DataFrame(result_rows) if result_rows else pd.DataFrame()
    
    def normalize_documents(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize documents table"""
        df_clean = df.copy()
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        result_rows = []
        for idx, row in df_clean.iterrows():
            ticker = normalize_string(row.get('ticker') or row.get('company'))
            if ticker:
                result_rows.append({
                    'company_id': ticker,
                    'year': None,
                    'doc_type': None,
                    'doc_url': normalize_string(row.get('link')) if pd.notna(row.get('link')) else None,
                    'filing_date': None
                })
        
        return pd.DataFrame(result_rows) if result_rows else pd.DataFrame()
    
    def normalize_prosandcons(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize prosandcons table"""
        df_clean = df.copy()
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        result_rows = []
        for idx, row in df_clean.iterrows():
            ticker = normalize_string(row.get('ticker') or row.get('company'))
            if ticker:
                result_rows.append({
                    'company_id': ticker,
                    'year': None,
                    'pros': normalize_string(row.get('pros')) if pd.notna(row.get('pros')) else None,
                    'cons': normalize_string(row.get('cons')) if pd.notna(row.get('cons')) else None
                })
        
        return pd.DataFrame(result_rows) if result_rows else pd.DataFrame()
    
    def normalize_financial_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize financial_ratios table"""
        df_clean = df.copy()
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        result_rows = []
        for idx, row in df_clean.iterrows():
            ticker = normalize_string(row.get('company_id'))
            year = normalize_year(row.get('year'))
            if ticker and year:
                result_rows.append({
                    'company_id': ticker,
                    'year': year,
                    'pe_ratio': normalize_numeric(row.get('pe_ratio')) if pd.notna(row.get('pe_ratio')) else None,
                    'pb_ratio': normalize_numeric(row.get('pb_ratio')) if pd.notna(row.get('pb_ratio')) else None,
                    'dividend_yield': normalize_numeric(row.get('dividend_yield_pct')) if pd.notna(row.get('dividend_yield_pct')) else None,
                    'peg_ratio': None,
                    'ev_ebitda': normalize_numeric(row.get('ev_ebitda')) if pd.notna(row.get('ev_ebitda')) else None
                })
        
        return pd.DataFrame(result_rows) if result_rows else pd.DataFrame()
    
    def normalize_peer_groups(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize peer_groups table"""
        df_clean = df.copy()
        df_clean.columns = df_clean.columns.str.lower().str.strip()
        
        result_rows = []
        for idx, row in df_clean.iterrows():
            ticker = normalize_string(row.get('company_id'))
            if ticker:
                result_rows.append({
                    'company_id': ticker,
                    'peer_company_id': None
                })
        
        return pd.DataFrame(result_rows) if result_rows else pd.DataFrame()
    
    def load_to_database(self, data_dict: Dict[str, pd.DataFrame]):
        """Load normalized data into SQLite database"""
        
        load_order = [
            ('sectors', self.normalize_sectors),
            ('companies', self.normalize_companies),
            ('profitandloss', self.normalize_profitandloss),
            ('balancesheet', self.normalize_balancesheet),
            ('cashflow', self.normalize_cashflow),
            ('analysis', self.normalize_analysis),
            ('stock_prices', self.normalize_stock_prices),
            ('documents', self.normalize_documents),
            ('prosandcons', self.normalize_prosandcons),
            ('financial_ratios', self.normalize_financial_ratios),
            ('peer_groups', self.normalize_peer_groups),
        ]
        
        for table_name, normalize_func in load_order:
            if table_name not in data_dict:
                print(f"Skipping {table_name}: not found")
                continue
            
            df = data_dict[table_name]
            df_normalized = normalize_func(df)
            
            rows_before = len(df)
            rows_after = len(df_normalized)
            rejections = rows_before - rows_after
            
            if rows_after == 0:
                print(f"Skipped {table_name}: no valid rows after normalization")
                continue
            
            try:
                df_normalized.to_sql(table_name, self.connection, if_exists='append', index=False)
                print(f"Loaded {table_name}: {rows_after} rows, {rejections} rejected")
                
                self.load_audit.append({
                    'table': table_name,
                    'rows_loaded': rows_after,
                    'rows_rejected': rejections,
                    'status': 'SUCCESS'
                })
            except Exception as e:
                print(f"Error loading {table_name}: {e}")
                self.load_audit.append({
                    'table': table_name,
                    'rows_loaded': 0,
                    'rows_rejected': rows_before,
                    'status': 'FAILED',
                    'error': str(e)
                })
    
    def verify_load(self) -> Dict[str, int]:
        """Verify row counts in each table"""
        cursor = self.connection.cursor()
        counts = {}
        
        tables = ['companies', 'sectors', 'profitandloss', 'balancesheet', 'cashflow',
                 'analysis', 'stock_prices', 'documents', 'prosandcons', 'financial_ratios',
                 'peer_groups']
        
        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                counts[table] = count
                print(f"  {table}: {count} rows")
            except Exception as e:
                print(f"  {table}: Error - {e}")
                counts[table] = 0
        
        return counts
    
    def check_fk_integrity(self) -> int:
        """Check foreign key integrity"""
        cursor = self.connection.cursor()
        total_violations = 0
        
        tables = ['profitandloss', 'balancesheet', 'cashflow', 'analysis',
                 'stock_prices', 'documents', 'prosandcons', 'financial_ratios', 'peer_groups']
        
        for table in tables:
            try:
                cursor.execute(f'PRAGMA foreign_key_check({table})')
                results = cursor.fetchall()
                if results:
                    total_violations += len(results)
                    print(f"  {table}: {len(results)} FK violations")
            except Exception as e:
                print(f"  {table}: Error checking FK - {e}")
        
        return total_violations
    
    def generate_audit_report(self, output_path: str):
        """Generate load audit CSV report"""
        audit_df = pd.DataFrame(self.load_audit)
        audit_df.to_csv(output_path, index=False)
        print(f"\nAudit report: {output_path}")
    
    def run(self, output_path: str = None):
        """Execute full loading pipeline"""
        print("Starting N100 Data Load Pipeline...")
        print("="*60)
        
        self.connect()
        
        print("\n1. Loading Excel files...")
        data_dict = self.load_all_files()
        print(f"   Total files loaded: {len(data_dict)}")
        
        print("\n2. Normalizing and loading to database...")
        self.load_to_database(data_dict)
        
        print("\n3. Verifying row counts...")
        row_counts = self.verify_load()
        
        print("\n4. Checking FK integrity...")
        fk_violations = self.check_fk_integrity()
        print(f"   Total FK violations: {fk_violations}")
        
        if output_path:
            self.generate_audit_report(output_path)
        
        self.disconnect()
        
        print("\n" + "="*60)
        print("LOAD COMPLETE")
        print("="*60)
        
        return row_counts, fk_violations


if __name__ == '__main__':
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / 'db' / 'nifty100.db'
    data_dir = project_root / 'data' / 'raw'
    output_dir = project_root / 'output'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_path = output_dir / 'load_audit.csv'
    
    loader = ExcelLoader(str(db_path), str(data_dir))
    row_counts, fk_violations = loader.run(str(audit_path))
