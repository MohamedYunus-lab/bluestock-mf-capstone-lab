"""
N100 CAGR Engine (Day 10)
CAGR with 6 edge case handlers for Revenue, PAT, EPS over 3/5/10-year periods
"""

from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CAGREdgeCase:
    """CAGR edge case metadata"""
    metric: str  # 'Revenue', 'PAT', 'EPS'
    period: int  # 3, 5, or 10
    edge_case: str
    flag: str
    value: Optional[float] = None
    beginning_value: Optional[float] = None
    ending_value: Optional[float] = None
    years_available: int = 0


class CAGREngine:
    """
    CAGR calculation with comprehensive edge case handling
    
    6 Edge Case Handlers:
    1. Turnarounds (negative to positive)
    2. Declines (positive to negative)
    3. Both negative (inception-to-exit both negative)
    4. Zero base (starting value is zero)
    5. Insufficient data (< required years)
    6. Missing or NaN values in series
    """
    
    @staticmethod
    def validate_series(values: List[Optional[float]]) -> Tuple[List[float], Optional[str]]:
        """
        Validate and clean a series of values
        Returns cleaned series and any validation issue
        """
        if not values:
            return [], "empty_series"
        
        clean_values = []
        for v in values:
            if v is None:
                return [], "contains_none"
            if v != v:  # NaN check
                return [], "contains_nan"
            clean_values.append(v)
        
        if len(clean_values) == 0:
            return [], "no_valid_values"
        
        return clean_values, None
    
    @staticmethod
    def calculate_cagr(beginning_value: float,
                      ending_value: float,
                      num_years: int) -> Tuple[Optional[float], Optional[CAGREdgeCase]]:
        """
        Core CAGR formula: ((Ending Value / Beginning Value) ^ (1/n)) - 1
        Where n is the number of years
        
        Returns:
            (cagr_percentage, edge_case_obj or None)
        
        Edge Cases Handled:
        1. TURNAROUND: beginning_value < 0 and ending_value > 0 → flag='turnaround'
        2. DECLINE: beginning_value > 0 and ending_value < 0 → flag='decline'
        3. BOTH_NEGATIVE: both values < 0 → flag='both_negative' (undefined CAGR)
        4. ZERO_BASE: beginning_value = 0 → flag='zero_base' (infinite CAGR)
        5. Insufficient years (checked by caller)
        6. Missing values (checked by caller)
        """
        edge_case = None
        
        # Edge Case 1: Turnaround (negative to positive)
        if beginning_value < 0 and ending_value > 0:
            edge_case = CAGREdgeCase(
                metric="",
                period=0,
                edge_case="turnaround",
                flag="TURNAROUND",
                beginning_value=beginning_value,
                ending_value=ending_value
            )
            return None, edge_case
        
        # Edge Case 2: Decline (positive to negative)
        if beginning_value > 0 and ending_value < 0:
            edge_case = CAGREdgeCase(
                metric="",
                period=0,
                edge_case="decline",
                flag="DECLINE",
                beginning_value=beginning_value,
                ending_value=ending_value
            )
            return None, edge_case
        
        # Edge Case 3: Both negative
        if beginning_value < 0 and ending_value < 0:
            edge_case = CAGREdgeCase(
                metric="",
                period=0,
                edge_case="both_negative",
                flag="BOTH_NEGATIVE",
                beginning_value=beginning_value,
                ending_value=ending_value
            )
            return None, edge_case
        
        # Edge Case 4: Zero base (division by zero)
        if beginning_value == 0:
            edge_case = CAGREdgeCase(
                metric="",
                period=0,
                edge_case="zero_base",
                flag="ZERO_BASE",
                beginning_value=beginning_value,
                ending_value=ending_value
            )
            return None, edge_case
        
        # Both values must be positive for valid CAGR
        if beginning_value <= 0 or ending_value <= 0:
            edge_case = CAGREdgeCase(
                metric="",
                period=0,
                edge_case="invalid_values",
                flag="INVALID"
            )
            return None, edge_case
        
        # Standard CAGR calculation
        try:
            cagr = ((ending_value / beginning_value) ** (1 / num_years) - 1) * 100
            return cagr, None
        except (ValueError, ZeroDivisionError) as e:
            edge_case = CAGREdgeCase(
                metric="",
                period=0,
                edge_case="calculation_error",
                flag="ERROR"
            )
            return None, edge_case
    
    @staticmethod
    def calculate_revenue_cagr(revenue_series: Dict[int, Optional[float]],
                              num_years: int = 5) -> Tuple[Optional[float], Optional[CAGREdgeCase]]:
        """
        Calculate Revenue CAGR over n-year period
        
        Args:
            revenue_series: Dict mapping year to revenue (e.g., {2019: 100, 2020: 120, ...})
            num_years: 3, 5, or 10
        
        Returns:
            (cagr_percentage, edge_case_obj or None)
        """
        if not revenue_series or len(revenue_series) < num_years + 1:
            edge_case = CAGREdgeCase(
                metric="Revenue",
                period=num_years,
                edge_case="insufficient_data",
                flag="INSUFFICIENT_DATA",
                years_available=len(revenue_series)
            )
            return None, edge_case
        
        years_sorted = sorted(revenue_series.keys())
        
        # Insufficient data check
        if len(years_sorted) < num_years + 1:
            edge_case = CAGREdgeCase(
                metric="Revenue",
                period=num_years,
                edge_case="insufficient_data",
                flag="INSUFFICIENT_DATA",
                years_available=len(years_sorted)
            )
            return None, edge_case
        
        # Get last num_years + 1 data points
        required_years = years_sorted[-num_years-1:]
        beginning_year = required_years[0]
        ending_year = required_years[-1]
        
        beginning_value = revenue_series.get(beginning_year)
        ending_value = revenue_series.get(ending_year)
        
        # Edge Case 5 & 6: Missing data
        if beginning_value is None or ending_value is None:
            edge_case = CAGREdgeCase(
                metric="Revenue",
                period=num_years,
                edge_case="missing_data",
                flag="MISSING_DATA"
            )
            return None, edge_case
        
        cagr, ec = CAGREngine.calculate_cagr(beginning_value, ending_value, num_years)
        
        if ec:
            ec.metric = "Revenue"
            ec.period = num_years
            ec.years_available = len(revenue_series)
        
        return cagr, ec
    
    @staticmethod
    def calculate_pat_cagr(pat_series: Dict[int, Optional[float]],
                          num_years: int = 5) -> Tuple[Optional[float], Optional[CAGREdgeCase]]:
        """
        Calculate PAT (Profit After Tax) CAGR over n-year period
        """
        if not pat_series or len(pat_series) < num_years + 1:
            edge_case = CAGREdgeCase(
                metric="PAT",
                period=num_years,
                edge_case="insufficient_data",
                flag="INSUFFICIENT_DATA",
                years_available=len(pat_series)
            )
            return None, edge_case
        
        years_sorted = sorted(pat_series.keys())
        
        if len(years_sorted) < num_years + 1:
            edge_case = CAGREdgeCase(
                metric="PAT",
                period=num_years,
                edge_case="insufficient_data",
                flag="INSUFFICIENT_DATA",
                years_available=len(years_sorted)
            )
            return None, edge_case
        
        required_years = years_sorted[-num_years-1:]
        beginning_year = required_years[0]
        ending_year = required_years[-1]
        
        beginning_value = pat_series.get(beginning_year)
        ending_value = pat_series.get(ending_year)
        
        if beginning_value is None or ending_value is None:
            edge_case = CAGREdgeCase(
                metric="PAT",
                period=num_years,
                edge_case="missing_data",
                flag="MISSING_DATA"
            )
            return None, edge_case
        
        cagr, ec = CAGREngine.calculate_cagr(beginning_value, ending_value, num_years)
        
        if ec:
            ec.metric = "PAT"
            ec.period = num_years
            ec.years_available = len(pat_series)
        
        return cagr, ec
    
    @staticmethod
    def calculate_eps_cagr(eps_series: Dict[int, Optional[float]],
                          num_years: int = 5) -> Tuple[Optional[float], Optional[CAGREdgeCase]]:
        """
        Calculate EPS (Earnings Per Share) CAGR over n-year period
        """
        if not eps_series or len(eps_series) < num_years + 1:
            edge_case = CAGREdgeCase(
                metric="EPS",
                period=num_years,
                edge_case="insufficient_data",
                flag="INSUFFICIENT_DATA",
                years_available=len(eps_series)
            )
            return None, edge_case
        
        years_sorted = sorted(eps_series.keys())
        
        if len(years_sorted) < num_years + 1:
            edge_case = CAGREdgeCase(
                metric="EPS",
                period=num_years,
                edge_case="insufficient_data",
                flag="INSUFFICIENT_DATA",
                years_available=len(years_sorted)
            )
            return None, edge_case
        
        required_years = years_sorted[-num_years-1:]
        beginning_year = required_years[0]
        ending_year = required_years[-1]
        
        beginning_value = eps_series.get(beginning_year)
        ending_value = eps_series.get(ending_year)
        
        if beginning_value is None or ending_value is None:
            edge_case = CAGREdgeCase(
                metric="EPS",
                period=num_years,
                edge_case="missing_data",
                flag="MISSING_DATA"
            )
            return None, edge_case
        
        cagr, ec = CAGREngine.calculate_cagr(beginning_value, ending_value, num_years)
        
        if ec:
            ec.metric = "EPS"
            ec.period = num_years
            ec.years_available = len(eps_series)
        
        return cagr, ec
