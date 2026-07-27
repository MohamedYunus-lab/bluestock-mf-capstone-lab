"""
N100 CAGR Engine (Day 10)
CAGR with 6 edge case handlers for Revenue, PAT, EPS over 3/5/10-year periods
"""

from typing import Optional, Dict, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CAGREdgeCase:
    """CAGR edge case metadata"""
    metric: str
    period: int
    edge_case: str
    flag: str
    value: Optional[float] = None
    years_available: int = 0


class CAGREngine:
    """CAGR calculation with 6 edge case handlers"""
    
    @staticmethod
    def calculate_cagr(beginning_value: float,
                      ending_value: float,
                      num_years: int) -> Tuple[Optional[float], Optional[CAGREdgeCase]]:
        """
        Core CAGR formula: ((Ending Value / Beginning Value) ^ (1/n)) - 1
        
        6 Edge Cases:
        1. TURNAROUND: negative to positive
        2. DECLINE: positive to negative
        3. BOTH_NEGATIVE: both < 0
        4. ZERO_BASE: beginning = 0
        5. Insufficient data (checked by caller)
        6. Missing values (checked by caller)
        """
        edge_case = None
        
        if beginning_value < 0 and ending_value > 0:
            edge_case = CAGREdgeCase("", 0, "turnaround", "TURNAROUND", years_available=num_years)
            return None, edge_case
        
        if beginning_value > 0 and ending_value < 0:
            edge_case = CAGREdgeCase("", 0, "decline", "DECLINE", years_available=num_years)
            return None, edge_case
        
        if beginning_value < 0 and ending_value < 0:
            edge_case = CAGREdgeCase("", 0, "both_negative", "BOTH_NEGATIVE", years_available=num_years)
            return None, edge_case
        
        if beginning_value == 0:
            edge_case = CAGREdgeCase("", 0, "zero_base", "ZERO_BASE", years_available=num_years)
            return None, edge_case
        
        if beginning_value <= 0 or ending_value <= 0:
            edge_case = CAGREdgeCase("", 0, "invalid_values", "INVALID", years_available=num_years)
            return None, edge_case
        
        try:
            cagr = ((ending_value / beginning_value) ** (1 / num_years) - 1) * 100
            return cagr, None
        except (ValueError, ZeroDivisionError):
            edge_case = CAGREdgeCase("", 0, "calculation_error", "ERROR", years_available=num_years)
            return None, edge_case
    
    @staticmethod
    def calculate_revenue_cagr(revenue_series: Dict[int, Optional[float]],
                              num_years: int = 5) -> Tuple[Optional[float], Optional[CAGREdgeCase]]:
        """Calculate Revenue CAGR over n-year period"""
        if not revenue_series or len(revenue_series) < num_years + 1:
            ec = CAGREdgeCase("Revenue", num_years, "insufficient_data", "INSUFFICIENT_DATA", 
                            years_available=len(revenue_series))
            return None, ec
        
        years_sorted = sorted(revenue_series.keys())
        
        if len(years_sorted) < num_years + 1:
            ec = CAGREdgeCase("Revenue", num_years, "insufficient_data", "INSUFFICIENT_DATA", 
                            years_available=len(years_sorted))
            return None, ec
        
        required_years = years_sorted[-num_years-1:]
        beginning_year = required_years[0]
        ending_year = required_years[-1]
        
        beginning_value = revenue_series.get(beginning_year)
        ending_value = revenue_series.get(ending_year)
        
        if beginning_value is None or ending_value is None:
            ec = CAGREdgeCase("Revenue", num_years, "missing_data", "MISSING_DATA",
                            years_available=len(years_sorted))
            return None, ec
        
        cagr, ec = CAGREngine.calculate_cagr(beginning_value, ending_value, num_years)
        
        if ec:
            ec.metric = "Revenue"
            ec.period = num_years
            ec.years_available = len(revenue_series)
        
        return cagr, ec
    
    @staticmethod
    def calculate_pat_cagr(pat_series: Dict[int, Optional[float]],
                          num_years: int = 5) -> Tuple[Optional[float], Optional[CAGREdgeCase]]:
        """Calculate PAT (Profit After Tax) CAGR over n-year period"""
        if not pat_series or len(pat_series) < num_years + 1:
            ec = CAGREdgeCase("PAT", num_years, "insufficient_data", "INSUFFICIENT_DATA",
                            years_available=len(pat_series))
            return None, ec
        
        years_sorted = sorted(pat_series.keys())
        
        if len(years_sorted) < num_years + 1:
            ec = CAGREdgeCase("PAT", num_years, "insufficient_data", "INSUFFICIENT_DATA",
                            years_available=len(years_sorted))
            return None, ec
        
        required_years = years_sorted[-num_years-1:]
        beginning_year = required_years[0]
        ending_year = required_years[-1]
        
        beginning_value = pat_series.get(beginning_year)
        ending_value = pat_series.get(ending_year)
        
        if beginning_value is None or ending_value is None:
            ec = CAGREdgeCase("PAT", num_years, "missing_data", "MISSING_DATA",
                            years_available=len(years_sorted))
            return None, ec
        
        cagr, ec = CAGREngine.calculate_cagr(beginning_value, ending_value, num_years)
        
        if ec:
            ec.metric = "PAT"
            ec.period = num_years
            ec.years_available = len(pat_series)
        
        return cagr, ec
    
    @staticmethod
    def calculate_eps_cagr(eps_series: Dict[int, Optional[float]],
                          num_years: int = 5) -> Tuple[Optional[float], Optional[CAGREdgeCase]]:
        """Calculate EPS (Earnings Per Share) CAGR over n-year period"""
        if not eps_series or len(eps_series) < num_years + 1:
            ec = CAGREdgeCase("EPS", num_years, "insufficient_data", "INSUFFICIENT_DATA",
                            years_available=len(eps_series))
            return None, ec
        
        years_sorted = sorted(eps_series.keys())
        
        if len(years_sorted) < num_years + 1:
            ec = CAGREdgeCase("EPS", num_years, "insufficient_data", "INSUFFICIENT_DATA",
                            years_available=len(years_sorted))
            return None, ec
        
        required_years = years_sorted[-num_years-1:]
        beginning_year = required_years[0]
        ending_year = required_years[-1]
        
        beginning_value = eps_series.get(beginning_year)
        ending_value = eps_series.get(ending_year)
        
        if beginning_value is None or ending_value is None:
            ec = CAGREdgeCase("EPS", num_years, "missing_data", "MISSING_DATA",
                            years_available=len(years_sorted))
            return None, ec
        
        cagr, ec = CAGREngine.calculate_cagr(beginning_value, ending_value, num_years)
        
        if ec:
            ec.metric = "EPS"
            ec.period = num_years
            ec.years_available = len(eps_series)
        
        return cagr, ec
