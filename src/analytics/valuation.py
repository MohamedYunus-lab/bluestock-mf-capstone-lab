"""
Valuation Module - FCF Yield, P/E Ratios, Overvaluation Flags
Day 26: Comprehensive valuation analysis with sector benchmarking
"""

import sqlite3
import pandas as pd
import logging
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)

DB_PATH = os.getenv('DB_PATH', 'c:/bluestock-mf-capstone/n100/db/nifty100.db')


@dataclass
class ValuationMetrics:
    """Valuation metrics for a company"""
    company_id: str
    company_name: str
    sector: str
    year: int
    
    # Absolute metrics
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    ev_ebitda: Optional[float]
    fcf_yield: Optional[float]
    
    # Relative metrics
    sector_median_pe: Optional[float]
    pe_to_sector_median: Optional[float]
    
    # Flags
    valuation_flag: str  # 'Discount', 'Fair', 'Caution'
    flag_confidence: float  # 0.0 to 1.0


class FCFYieldCalculator:
    """Calculate FCF Yield for companies"""
    
    @staticmethod
    def calculate_fcf_yield(
        free_cash_flow_cr: Optional[float],
        market_cap_cr: Optional[float]
    ) -> Optional[float]:
        """
        FCF Yield = (Free Cash Flow / Market Cap) * 100
        
        Args:
            free_cash_flow_cr: Free cash flow in crores
            market_cap_cr: Market cap in crores
        
        Returns:
            FCF Yield percentage or None
        """
        if free_cash_flow_cr is None or market_cap_cr is None:
            return None
        
        if market_cap_cr <= 0:
            return None
        
        fcf_yield = (free_cash_flow_cr / market_cap_cr) * 100
        return fcf_yield
    
    @staticmethod
    def calculate_fcf_to_equity(
        free_cash_flow_cr: Optional[float],
        equity_value_cr: Optional[float]
    ) -> Optional[float]:
        """FCF to Equity = Free Cash Flow / Equity Value"""
        if free_cash_flow_cr is None or equity_value_cr is None:
            return None
        
        if equity_value_cr <= 0:
            return None
        
        return (free_cash_flow_cr / equity_value_cr) * 100


class SectorMedianCalculator:
    """Calculate sector-level median metrics"""
    
    @staticmethod
    def get_sector_median_pe(sector_id: str, year: int) -> Optional[float]:
        """Get median P/E for sector in given year"""
        conn = sqlite3.connect(DB_PATH)
        
        query = """
        SELECT AVG(fr.pe_ratio) as median_pe
        FROM financial_ratios fr
        JOIN companies c ON fr.company_id = c.company_id
        WHERE c.sector_id = ? AND fr.year = ? AND fr.pe_ratio > 0
        """
        
        cursor = conn.execute(query, (sector_id, year))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return result[0]
        return None
    
    @staticmethod
    def get_sector_median_pb(sector_id: str, year: int) -> Optional[float]:
        """Get median P/B for sector in given year"""
        conn = sqlite3.connect(DB_PATH)
        
        query = """
        SELECT AVG(fr.pb_ratio) as median_pb
        FROM financial_ratios fr
        JOIN companies c ON fr.company_id = c.company_id
        WHERE c.sector_id = ? AND fr.year = ? AND fr.pb_ratio > 0
        """
        
        cursor = conn.execute(query, (sector_id, year))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return result[0]
        return None
    
    @staticmethod
    def get_sector_median_ev_ebitda(sector_id: str, year: int) -> Optional[float]:
        """Get median EV/EBITDA for sector in given year"""
        conn = sqlite3.connect(DB_PATH)
        
        query = """
        SELECT AVG(fr.ev_ebitda) as median_ev_ebitda
        FROM financial_ratios fr
        JOIN companies c ON fr.company_id = c.company_id
        WHERE c.sector_id = ? AND fr.year = ? AND fr.ev_ebitda > 0
        """
        
        cursor = conn.execute(query, (sector_id, year))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return result[0]
        return None


class ValuationFlagger:
    """Generate overvaluation/undervaluation flags"""
    
    @staticmethod
    def flag_pe_valuation(
        pe_ratio: Optional[float],
        sector_median_pe: Optional[float]
    ) -> Tuple[str, float]:
        """
        Flag company valuation based on P/E vs sector median
        
        Rules:
        - P/E > 1.5x median = Caution (Overvalued)
        - P/E < 0.7x median = Discount (Undervalued)
        - 0.7x to 1.5x = Fair (Fairly valued)
        
        Returns:
            Tuple of (flag, confidence)
        """
        if pe_ratio is None or sector_median_pe is None or sector_median_pe <= 0:
            return 'Fair', 0.5
        
        pe_to_median = pe_ratio / sector_median_pe
        
        if pe_to_median > 1.5:
            confidence = min(0.95, 0.7 + (pe_to_median - 1.5) * 0.1)
            return 'Caution', confidence
        
        elif pe_to_median < 0.7:
            confidence = min(0.95, 0.7 + (0.7 - pe_to_median) * 0.2)
            return 'Discount', confidence
        
        else:
            confidence = 0.85
            return 'Fair', confidence
    
    @staticmethod
    def flag_combined_valuation(
        pe_ratio: Optional[float],
        pb_ratio: Optional[float],
        ev_ebitda: Optional[float],
        fcf_yield: Optional[float],
        sector_median_pe: Optional[float],
        sector_median_pb: Optional[float],
        sector_median_ev_ebitda: Optional[float]
    ) -> Tuple[str, float]:
        """
        Combined valuation flag using multiple metrics
        
        Returns:
            Tuple of (flag, confidence)
        """
        flags = {}
        weights = {}
        
        # P/E Flag
        if pe_ratio and sector_median_pe:
            flag, conf = ValuationFlagger.flag_pe_valuation(pe_ratio, sector_median_pe)
            flags['pe'] = flag
            weights['pe'] = 0.4
        
        # P/B Flag
        if pb_ratio and sector_median_pb and sector_median_pb > 0:
            pb_to_median = pb_ratio / sector_median_pb
            if pb_to_median > 1.5:
                flags['pb'] = 'Caution'
            elif pb_to_median < 0.7:
                flags['pb'] = 'Discount'
            else:
                flags['pb'] = 'Fair'
            weights['pb'] = 0.3
        
        # EV/EBITDA Flag
        if ev_ebitda and sector_median_ev_ebitda and sector_median_ev_ebitda > 0:
            ev_to_median = ev_ebitda / sector_median_ev_ebitda
            if ev_to_median > 1.5:
                flags['ev'] = 'Caution'
            elif ev_to_median < 0.7:
                flags['ev'] = 'Discount'
            else:
                flags['ev'] = 'Fair'
            weights['ev'] = 0.3
        
        # FCF Yield (higher is better)
        if fcf_yield:
            if fcf_yield > 8:
                flags['fcf'] = 'Discount'
            elif fcf_yield > 5:
                flags['fcf'] = 'Fair'
            else:
                flags['fcf'] = 'Caution'
            weights['fcf'] = 0.2
        
        # Aggregate
        if not flags:
            return 'Fair', 0.5
        
        # Count votes
        caution_votes = sum(w for k, w in weights.items() if flags.get(k) == 'Caution')
        discount_votes = sum(w for k, w in weights.items() if flags.get(k) == 'Discount')
        fair_votes = sum(w for k, w in weights.items() if flags.get(k) == 'Fair')
        
        total_weight = sum(weights.values())
        
        if caution_votes > fair_votes and caution_votes > discount_votes:
            confidence = min(0.95, caution_votes / total_weight)
            return 'Caution', confidence
        
        elif discount_votes > fair_votes and discount_votes > caution_votes:
            confidence = min(0.95, discount_votes / total_weight)
            return 'Discount', confidence
        
        else:
            confidence = 0.75
            return 'Fair', confidence


def get_valuation_metrics(company_id: str, year: int) -> Optional[ValuationMetrics]:
    """Get complete valuation metrics for company"""
    conn = sqlite3.connect(DB_PATH)
    
    # Get company and ratio data
    query = """
    SELECT 
        c.company_id,
        c.company_name,
        s.sector_id,
        s.sector_name,
        fr.pe_ratio,
        fr.pb_ratio,
        fr.ev_ebitda,
        cf.free_cash_flow_cr,
        c.market_cap_inr
    FROM companies c
    LEFT JOIN sectors s ON c.sector_id = s.sector_id
    LEFT JOIN financial_ratios fr ON c.company_id = fr.company_id AND fr.year = ?
    LEFT JOIN cashflow cf ON c.company_id = cf.company_id AND cf.year = ?
    WHERE c.company_id = ?
    """
    
    cursor = conn.execute(query, (year, year, company_id))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    (company_id, company_name, sector_id, sector_name, pe_ratio, pb_ratio, 
     ev_ebitda, fcf_cr, market_cap_inr) = result
    
    # Calculate FCF Yield
    market_cap_cr = (market_cap_inr / 1e7) if market_cap_inr else None  # Convert to crores
    fcf_yield = FCFYieldCalculator.calculate_fcf_yield(fcf_cr, market_cap_cr)
    
    # Get sector median P/E
    sector_median_pe = SectorMedianCalculator.get_sector_median_pe(sector_id, year)
    sector_median_pb = SectorMedianCalculator.get_sector_median_pb(sector_id, year)
    sector_median_ev = SectorMedianCalculator.get_sector_median_ev_ebitda(sector_id, year)
    
    # Calculate P/E to median ratio
    pe_to_sector_median = None
    if pe_ratio and sector_median_pe and sector_median_pe > 0:
        pe_to_sector_median = pe_ratio / sector_median_pe
    
    # Generate flags
    flag, confidence = ValuationFlagger.flag_combined_valuation(
        pe_ratio, pb_ratio, ev_ebitda, fcf_yield,
        sector_median_pe, sector_median_pb, sector_median_ev
    )
    
    return ValuationMetrics(
        company_id=company_id,
        company_name=company_name,
        sector=sector_name or 'Unknown',
        year=year,
        pe_ratio=pe_ratio,
        pb_ratio=pb_ratio,
        ev_ebitda=ev_ebitda,
        fcf_yield=fcf_yield,
        sector_median_pe=sector_median_pe,
        pe_to_sector_median=pe_to_sector_median,
        valuation_flag=flag,
        flag_confidence=confidence
    )


def generate_valuation_summary(year: int, output_path: str = None) -> pd.DataFrame:
    """
    Generate valuation summary for all 92 companies
    
    Output: DataFrame with 92 rows
    """
    conn = sqlite3.connect(DB_PATH)
    
    # Get all companies
    query = "SELECT company_id FROM companies ORDER BY company_name"
    companies_df = pd.read_sql_query(query, conn)
    conn.close()
    
    results = []
    
    for _, company_row in companies_df.iterrows():
        company_id = company_row['company_id']
        metrics = get_valuation_metrics(company_id, year)
        
        if metrics:
            results.append({
                'Company ID': metrics.company_id,
                'Company Name': metrics.company_name,
                'Sector': metrics.sector,
                'Year': metrics.year,
                'P/E Ratio': f"{metrics.pe_ratio:.2f}" if metrics.pe_ratio else "N/A",
                'P/B Ratio': f"{metrics.pb_ratio:.2f}" if metrics.pb_ratio else "N/A",
                'EV/EBITDA': f"{metrics.ev_ebitda:.2f}" if metrics.ev_ebitda else "N/A",
                'FCF Yield (%)': f"{metrics.fcf_yield:.2f}" if metrics.fcf_yield else "N/A",
                'Sector Median P/E': f"{metrics.sector_median_pe:.2f}" if metrics.sector_median_pe else "N/A",
                'P/E vs Sector (%)': f"{((metrics.pe_to_sector_median - 1) * 100):.1f}" if metrics.pe_to_sector_median else "N/A",
                'Valuation Flag': metrics.valuation_flag,
                'Flag Confidence': f"{metrics.flag_confidence:.2%}"
            })
    
    df_summary = pd.DataFrame(results)
    
    if output_path:
        df_summary.to_excel(output_path, index=False)
        logger.info(f"Valuation summary written to {output_path}")
    
    return df_summary


def generate_valuation_flags(year: int, output_path: str = None) -> pd.DataFrame:
    """
    Generate valuation flags for Caution/Discount companies only
    """
    summary_df = generate_valuation_summary(year)
    
    # Filter for Caution and Discount flags
    flags_df = summary_df[
        summary_df['Valuation Flag'].isin(['Caution', 'Discount'])
    ].copy()
    
    flags_df = flags_df.sort_values('Valuation Flag')
    
    if output_path:
        flags_df.to_csv(output_path, index=False)
        logger.info(f"Valuation flags written to {output_path}")
    
    return flags_df
