"""
Data Quality Validator
Implements 16 data quality rules (DQ-01 to DQ-16)
"""

import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime


class DataQualityValidator:
    """Data Quality Validation Engine"""
    
    def __init__(self):
        self.failures = []
        self.warnings = []
    
    def validate_all(self, data_dict: Dict[str, pd.DataFrame]) -> Tuple[List, List]:
        """Run all 16 DQ rules"""
        
        self.dq_01_company_pk_uniqueness(data_dict.get('companies', pd.DataFrame()))
        self.dq_02_company_year_pk(data_dict.get('profitandloss', pd.DataFrame()))
        self.dq_03_fk_integrity(data_dict)
        self.dq_04_bs_balance_check(data_dict.get('balancesheet', pd.DataFrame()))
        self.dq_05_opm_crosscheck(data_dict.get('profitandloss', pd.DataFrame()))
        self.dq_06_positive_sales(data_dict.get('profitandloss', pd.DataFrame()))
        self.dq_07_year_range_valid(data_dict)
        self.dq_08_revenue_consistency(data_dict.get('profitandloss', pd.DataFrame()))
        self.dq_09_net_cash_change(data_dict.get('cashflow', pd.DataFrame()))
        self.dq_10_tax_rate_valid(data_dict.get('profitandloss', pd.DataFrame()))
        self.dq_11_dividend_yield_valid(data_dict.get('financial_ratios', pd.DataFrame()))
        self.dq_12_url_format(data_dict.get('documents', pd.DataFrame()))
        self.dq_13_eps_sign(data_dict.get('profitandloss', pd.DataFrame()))
        self.dq_14_bse_balance_sheet(data_dict.get('balancesheet', pd.DataFrame()))
        self.dq_15_debt_coverage_ratio(data_dict.get('analysis', pd.DataFrame()))
        self.dq_16_pe_ratio_valid(data_dict.get('financial_ratios', pd.DataFrame()))
        
        return self.failures, self.warnings
    
    def dq_01_company_pk_uniqueness(self, df: pd.DataFrame):
        """DQ-01: Company ID must be unique"""
        if df.empty:
            return
        
        duplicates = df[df['company_id'].duplicated(keep=False)]
        if not duplicates.empty:
            for idx, row in duplicates.iterrows():
                self.failures.append({
                    'rule': 'DQ-01',
                    'severity': 'CRITICAL',
                    'table': 'companies',
                    'row': idx,
                    'message': f"Duplicate company_id: {row['company_id']}"
                })
    
    def dq_02_company_year_pk(self, df: pd.DataFrame):
        """DQ-02: (company_id, year) must be unique in fact tables"""
        if df.empty:
            return
        
        if 'company_id' not in df.columns or 'year' not in df.columns:
            return
        
        duplicates = df[df.duplicated(subset=['company_id', 'year'], keep=False)]
        if not duplicates.empty:
            for idx, row in duplicates.iterrows():
                self.failures.append({
                    'rule': 'DQ-02',
                    'severity': 'CRITICAL',
                    'table': df.name if hasattr(df, 'name') else 'unknown',
                    'row': idx,
                    'message': f"Duplicate (company_id, year): {row['company_id']}, {row['year']}"
                })
    
    def dq_03_fk_integrity(self, data_dict: Dict[str, pd.DataFrame]):
        """DQ-03: Foreign key integrity checks"""
        companies = data_dict.get('companies', pd.DataFrame())
        if companies.empty:
            return
        
        valid_company_ids = set(companies['company_id'])
        
        for table_name in ['profitandloss', 'balancesheet', 'cashflow', 'analysis', 'stock_prices', 'documents']:
            df = data_dict.get(table_name, pd.DataFrame())
            if df.empty or 'company_id' not in df.columns:
                continue
            
            invalid = df[~df['company_id'].isin(valid_company_ids)]
            for idx, row in invalid.iterrows():
                self.failures.append({
                    'rule': 'DQ-03',
                    'severity': 'CRITICAL',
                    'table': table_name,
                    'row': idx,
                    'message': f"FK violation: company_id {row['company_id']} not in companies"
                })
    
    def dq_04_bs_balance_check(self, df: pd.DataFrame):
        """DQ-04: Assets = Liabilities + Equity (within 1%)"""
        if df.empty or 'total_assets_cr' not in df.columns:
            return
        
        df_copy = df.copy()
        df_copy['total_liabilities_cr'] = df_copy['total_liabilities_cr'].fillna(0)
        df_copy['equity_cr'] = df_copy['equity_cr'].fillna(0)
        
        df_copy['calculated_liab_equity'] = df_copy['total_liabilities_cr'] + df_copy['equity_cr']
        df_copy['variance'] = abs(df_copy['total_assets_cr'] - df_copy['calculated_liab_equity']) / (df_copy['total_assets_cr'] + 1)
        
        violations = df_copy[df_copy['variance'] > 0.01]
        for idx, row in violations.iterrows():
            self.warnings.append({
                'rule': 'DQ-04',
                'severity': 'WARNING',
                'table': 'balancesheet',
                'row': idx,
                'message': f"BS imbalance: Assets {row['total_assets_cr']} != L+E {row['calculated_liab_equity']}"
            })
    
    def dq_05_opm_crosscheck(self, df: pd.DataFrame):
        """DQ-05: OPM = Operating Profit / Revenue"""
        if df.empty or 'operating_profit_cr' not in df.columns or 'revenue_cr' not in df.columns:
            return
        
        df_copy = df[(df['revenue_cr'] > 0) & (df['opm'].notna())].copy()
        df_copy['calculated_opm'] = df_copy['operating_profit_cr'] / df_copy['revenue_cr']
        df_copy['variance'] = abs(df_copy['opm'] - df_copy['calculated_opm'])
        
        violations = df_copy[df_copy['variance'] > 0.01]
        for idx, row in violations.iterrows():
            self.warnings.append({
                'rule': 'DQ-05',
                'severity': 'WARNING',
                'table': 'profitandloss',
                'row': idx,
                'message': f"OPM mismatch: Reported {row['opm']}, Calculated {row['calculated_opm']}"
            })
    
    def dq_06_positive_sales(self, df: pd.DataFrame):
        """DQ-06: Revenue must be positive"""
        if df.empty or 'revenue_cr' not in df.columns:
            return
        
        negative = df[(df['revenue_cr'] < 0) | (df['revenue_cr'] == 0)]
        for idx, row in negative.iterrows():
            self.failures.append({
                'rule': 'DQ-06',
                'severity': 'CRITICAL',
                'table': 'profitandloss',
                'row': idx,
                'message': f"Revenue must be positive: {row['revenue_cr']}"
            })
    
    def dq_07_year_range_valid(self, data_dict: Dict[str, pd.DataFrame]):
        """DQ-07: Year must be between 2000 and current year"""
        current_year = datetime.now().year
        
        for table_name in ['profitandloss', 'balancesheet', 'cashflow', 'analysis', 'financial_ratios']:
            df = data_dict.get(table_name, pd.DataFrame())
            if df.empty or 'year' not in df.columns:
                continue
            
            invalid = df[(df['year'] < 2000) | (df['year'] > current_year + 1)]
            for idx, row in invalid.iterrows():
                self.failures.append({
                    'rule': 'DQ-07',
                    'severity': 'CRITICAL',
                    'table': table_name,
                    'row': idx,
                    'message': f"Year out of range: {row['year']}"
                })
    
    def dq_08_revenue_consistency(self, df: pd.DataFrame):
        """DQ-08: Revenue should increase or stay similar YoY"""
        if df.empty or 'revenue_cr' not in df.columns:
            return
        
        df_sorted = df.sort_values(['company_id', 'year']).copy()
        df_sorted['prev_revenue'] = df_sorted.groupby('company_id')['revenue_cr'].shift(1)
        
        df_sorted['decline_pct'] = ((df_sorted['prev_revenue'] - df_sorted['revenue_cr']) / df_sorted['prev_revenue']).abs()
        violations = df_sorted[df_sorted['decline_pct'] > 0.50]
        
        for idx, row in violations.iterrows():
            if pd.notna(row['prev_revenue']):
                self.warnings.append({
                    'rule': 'DQ-08',
                    'severity': 'WARNING',
                    'table': 'profitandloss',
                    'row': idx,
                    'message': f"Large revenue change: {row['prev_revenue']} to {row['revenue_cr']}"
                })
    
    def dq_09_net_cash_change(self, df: pd.DataFrame):
        """DQ-09: Net cash change = OCF + ICF + FCF"""
        if df.empty or 'net_cash_change_cr' not in df.columns:
            return
        
        df_copy = df.copy()
        df_copy['operating_cf_cr'] = df_copy['operating_cf_cr'].fillna(0)
        df_copy['investing_cf_cr'] = df_copy['investing_cf_cr'].fillna(0)
        df_copy['financing_cf_cr'] = df_copy['financing_cf_cr'].fillna(0)
        
        df_copy['calculated'] = df_copy['operating_cf_cr'] + df_copy['investing_cf_cr'] + df_copy['financing_cf_cr']
        df_copy['variance'] = abs(df_copy['net_cash_change_cr'] - df_copy['calculated'])
        
        violations = df_copy[df_copy['variance'] > 1]
        for idx, row in violations.iterrows():
            self.warnings.append({
                'rule': 'DQ-09',
                'severity': 'WARNING',
                'table': 'cashflow',
                'row': idx,
                'message': f"Net cash mismatch: {row['net_cash_change_cr']} vs {row['calculated']}"
            })
    
    def dq_10_tax_rate_valid(self, df: pd.DataFrame):
        """DQ-10: Tax rate should be 0-60%"""
        if df.empty or 'tax_expense_cr' not in df.columns or 'net_profit_cr' not in df.columns:
            return
        
        df_copy = df[df['net_profit_cr'] > 0].copy()
        if df_copy.empty:
            return
        
        df_copy['tax_rate'] = df_copy['tax_expense_cr'] / (df_copy['net_profit_cr'] + df_copy['tax_expense_cr'])
        violations = df_copy[(df_copy['tax_rate'] < 0) | (df_copy['tax_rate'] > 0.60)]
        
        for idx, row in violations.iterrows():
            self.warnings.append({
                'rule': 'DQ-10',
                'severity': 'WARNING',
                'table': 'profitandloss',
                'row': idx,
                'message': f"Tax rate unusual: {row['tax_rate']:.2%}"
            })
    
    def dq_11_dividend_yield_valid(self, df: pd.DataFrame):
        """DQ-11: Dividend yield should be 0-20%"""
        if df.empty or 'dividend_yield' not in df.columns:
            return
        
        violations = df[(df['dividend_yield'] < 0) | (df['dividend_yield'] > 0.20)]
        for idx, row in violations.iterrows():
            self.warnings.append({
                'rule': 'DQ-11',
                'severity': 'WARNING',
                'table': 'financial_ratios',
                'row': idx,
                'message': f"Dividend yield unusual: {row['dividend_yield']:.2%}"
            })
    
    def dq_12_url_format(self, df: pd.DataFrame):
        """DQ-12: Document URLs should be valid format"""
        if df.empty or 'doc_url' not in df.columns:
            return
        
        invalid = df[~df['doc_url'].str.startswith('http', na=False)]
        for idx, row in invalid.iterrows():
            if pd.notna(row['doc_url']):
                self.warnings.append({
                    'rule': 'DQ-12',
                    'severity': 'WARNING',
                    'table': 'documents',
                    'row': idx,
                    'message': f"Invalid URL format: {row['doc_url']}"
                })
    
    def dq_13_eps_sign(self, df: pd.DataFrame):
        """DQ-13: EPS sign should match net profit sign"""
        if df.empty or 'eps' not in df.columns or 'net_profit_cr' not in df.columns:
            return
        
        df_copy = df[(df['eps'].notna()) & (df['net_profit_cr'].notna())].copy()
        violations = df_copy[((df_copy['eps'] > 0) & (df_copy['net_profit_cr'] < 0)) |
                             ((df_copy['eps'] < 0) & (df_copy['net_profit_cr'] > 0))]
        
        for idx, row in violations.iterrows():
            self.failures.append({
                'rule': 'DQ-13',
                'severity': 'CRITICAL',
                'table': 'profitandloss',
                'row': idx,
                'message': f"EPS sign mismatch: EPS {row['eps']}, NP {row['net_profit_cr']}"
            })
    
    def dq_14_bse_balance_sheet(self, df: pd.DataFrame):
        """DQ-14: Balance sheet items should be non-negative"""
        if df.empty:
            return
        
        numeric_cols = ['total_assets_cr', 'current_assets_cr', 'fixed_assets_cr',
                       'total_liabilities_cr', 'current_liabilities_cr', 'equity_cr']
        
        for col in numeric_cols:
            if col in df.columns:
                violations = df[df[col] < 0]
                for idx, row in violations.iterrows():
                    self.warnings.append({
                        'rule': 'DQ-14',
                        'severity': 'WARNING',
                        'table': 'balancesheet',
                        'row': idx,
                        'message': f"Negative balance sheet item {col}: {row[col]}"
                    })
    
    def dq_15_debt_coverage_ratio(self, df: pd.DataFrame):
        """DQ-15: Debt to EBITDA should be reasonable"""
        if df.empty or 'debt_to_ebitda' not in df.columns:
            return
        
        violations = df[(df['debt_to_ebitda'] < 0) | (df['debt_to_ebitda'] > 20)]
        for idx, row in violations.iterrows():
            if pd.notna(row['debt_to_ebitda']):
                self.warnings.append({
                    'rule': 'DQ-15',
                    'severity': 'WARNING',
                    'table': 'analysis',
                    'row': idx,
                    'message': f"Unusual debt to EBITDA: {row['debt_to_ebitda']}"
                })
    
    def dq_16_pe_ratio_valid(self, df: pd.DataFrame):
        """DQ-16: PE ratio should be positive and reasonable"""
        if df.empty or 'pe_ratio' not in df.columns:
            return
        
        violations = df[(df['pe_ratio'] < 0) | (df['pe_ratio'] > 500)]
        for idx, row in violations.iterrows():
            if pd.notna(row['pe_ratio']):
                self.warnings.append({
                    'rule': 'DQ-16',
                    'severity': 'WARNING',
                    'table': 'financial_ratios',
                    'row': idx,
                    'message': f"Unusual PE ratio: {row['pe_ratio']}"
                })
    
    def generate_report(self) -> pd.DataFrame:
        """Generate validation failure report"""
        all_issues = self.failures + self.warnings
        if not all_issues:
            return pd.DataFrame()
        
        report = pd.DataFrame(all_issues)
        report['timestamp'] = datetime.now()
        return report
