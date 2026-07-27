"""
N100 Cashflow KPIs & Capital Allocation (Day 11)
CFO quality, CapEx intensity, FCF conversion, 8-pattern capital allocation classifier
"""

from typing import Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CapitalAllocationPattern(Enum):
    """8 patterns of capital allocation"""
    REINVESTMENT = "Reinvestment"
    SHAREHOLDER_RETURNS = "Shareholder Returns"
    DELEVERAGING = "Deleveraging"
    DEBT_ACCUMULATION = "Debt Accumulation"
    GROWTH_FOCUSED = "Growth Focused"
    CONSERVATIVE = "Conservative"
    BALANCED = "Balanced"
    OPPORTUNISTIC = "Opportunistic"


@dataclass
class CapitalAllocationResult:
    """Capital allocation classification result"""
    pattern: str
    confidence: float
    reasoning: str
    capex_intensity: float
    fcf_conversion: float


class CashflowQualityMetrics:
    """Day 11: Cashflow quality and efficiency ratios"""
    
    @staticmethod
    def free_cash_flow(operating_cf_cr: Optional[float],
                      capex_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """FCF = Operating Cash Flow - CapEx"""
        if operating_cf_cr is None or capex_cr is None:
            return None, "missing_data"
        
        fcf = operating_cf_cr - capex_cr
        return fcf, None
    
    @staticmethod
    def cfo_quality_score(operating_cf_cr: Optional[float],
                         net_income_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """CFO Quality = Operating CF / PAT ratio"""
        if operating_cf_cr is None or net_income_cr is None:
            return None, "missing_data"
        
        if net_income_cr == 0:
            return None, "zero_net_income"
        
        if net_income_cr < 0:
            return None, "negative_net_income"
        
        ratio = operating_cf_cr / net_income_cr
        return ratio, None
    
    @staticmethod
    def capex_intensity(capex_cr: Optional[float],
                       revenue_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """CapEx Intensity = (Capital Expenditure / Revenue) * 100"""
        if capex_cr is None or revenue_cr is None:
            return None, "missing_data"
        
        if revenue_cr == 0:
            return None, "zero_revenue"
        
        if capex_cr < 0:
            return None, "negative_capex"
        
        intensity = (capex_cr / revenue_cr) * 100
        return intensity, None
    
    @staticmethod
    def fcf_conversion_ratio(free_cash_flow_cr: Optional[float],
                            net_income_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """FCF Conversion = Free Cash Flow / Net Income"""
        if free_cash_flow_cr is None or net_income_cr is None:
            return None, "missing_data"
        
        if net_income_cr == 0:
            return None, "zero_net_income"
        
        if net_income_cr < 0:
            return None, "negative_net_income"
        
        conversion = free_cash_flow_cr / net_income_cr
        return conversion, None


class CapitalAllocationClassifier:
    """Day 11: 8-pattern capital allocation classifier"""
    
    @staticmethod
    def classify_capital_allocation(fcf_cr: Optional[float],
                                   capex_cr: Optional[float],
                                   dividend_paid_cr: Optional[float],
                                   net_income_cr: Optional[float],
                                   revenue_cr: Optional[float]) -> CapitalAllocationResult:
        """Classify capital allocation into 8 patterns"""
        
        if fcf_cr is None or capex_cr is None or net_income_cr is None or revenue_cr is None:
            return CapitalAllocationResult(
                pattern="Opportunistic",
                confidence=0.0,
                reasoning="Insufficient data",
                capex_intensity=0.0,
                fcf_conversion=0.0
            )
        
        capex_intensity = (capex_cr / revenue_cr) * 100 if revenue_cr > 0 else 0
        fcf_conversion = fcf_cr / net_income_cr if net_income_cr > 0 else 0
        dividend_paid = dividend_paid_cr or 0
        
        pattern, confidence, reasoning = CapitalAllocationClassifier._classify_pattern(
            fcf_cr, capex_cr, dividend_paid, capex_intensity, fcf_conversion
        )
        
        return CapitalAllocationResult(
            pattern=pattern,
            confidence=confidence,
            reasoning=reasoning,
            capex_intensity=capex_intensity,
            fcf_conversion=fcf_conversion
        )
    
    @staticmethod
    def _classify_pattern(fcf_cr: float, capex_cr: float, dividend_paid: float,
                         capex_intensity: float, fcf_conversion: float) -> Tuple[str, float, str]:
        """Internal classification logic"""
        
        if capex_intensity > 15 and dividend_paid < capex_cr * 0.1:
            return ("Reinvestment", 0.85,
                   f"High CapEx intensity ({capex_intensity:.1f}%), minimal shareholder returns")
        
        if capex_intensity < 5 and dividend_paid > 0:
            return ("Shareholder Returns", 0.85,
                   f"Low CapEx ({capex_intensity:.1f}%), high dividend payout")
        
        if fcf_cr > 0 and capex_cr < fcf_cr * 0.1 and dividend_paid > fcf_cr * 0.5:
            return ("Deleveraging", 0.80,
                   f"FCF prioritized for debt reduction and shareholder returns")
        
        if fcf_cr < 0 and capex_cr > 0:
            return ("Debt Accumulation", 0.80,
                   f"Negative FCF ({fcf_cr:.1f}) with CapEx spending")
        
        if fcf_cr > 0 and capex_cr > fcf_cr * 0.7 and dividend_paid < fcf_cr * 0.1:
            return ("Growth Focused", 0.80,
                   f"FCF deployed into CapEx ({capex_intensity:.1f}%)")
        
        if fcf_cr > 0 and capex_cr < fcf_cr * 0.1 and dividend_paid < fcf_cr * 0.1:
            return ("Conservative", 0.75,
                   f"Positive FCF ({fcf_cr:.1f}) with minimal deployment")
        
        if fcf_cr > 0 and 0.2 < capex_cr / fcf_cr < 0.6:
            return ("Balanced", 0.80,
                   "Balanced allocation between CapEx and returns")
        
        return ("Opportunistic", 0.60,
               "Capital allocation pattern does not fit standard categories")
