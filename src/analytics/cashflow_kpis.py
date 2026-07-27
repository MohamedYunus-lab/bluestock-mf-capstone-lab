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
    REINVESTMENT = "reinvestment"  # High CapEx, low dividend
    SHAREHOLDER_RETURNS = "shareholder_returns"  # Low CapEx, high dividend/buyback
    DELEVERAGING = "deleveraging"  # High FCF, increasing debt repayment
    DEBT_ACCUMULATION = "debt_accumulation"  # FCF used for debt, not growth
    GROWTH_FOCUSED = "growth_focused"  # All FCF into CapEx
    CONSERVATIVE = "conservative"  # Accumulating cash, minimal deployment
    BALANCED = "balanced"  # Balanced between growth, returns, debt reduction
    OPPORTUNISTIC = "opportunistic"  # M&A or acquisitions (no clear pattern)


@dataclass
class CashflowMetric:
    """Cashflow KPI result with metadata"""
    metric_name: str
    value: Optional[float]
    label: str = ""
    edge_case: Optional[str] = None


@dataclass
class CapitalAllocationResult:
    """Capital allocation classification result"""
    pattern: CapitalAllocationPattern
    confidence: float  # 0.0 to 1.0
    reasoning: str
    capex_intensity: float
    fcf_conversion: float
    dividend_payout_ratio: Optional[float]


class CashflowQualityMetrics:
    """Day 11: Cashflow quality and efficiency ratios"""
    
    @staticmethod
    def operating_cash_flow_to_sales(operating_cf_cr: Optional[float],
                                     revenue_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """
        OCF to Sales = Operating Cash Flow / Revenue
        Measures quality of earnings - how much revenue converts to cash
        
        Good companies: > 10% (means revenue quality is high)
        """
        edge_case = None
        
        if operating_cf_cr is None or revenue_cr is None:
            return None, "missing_data"
        
        if revenue_cr == 0:
            return None, "zero_revenue"
        
        if operating_cf_cr < 0:
            return None, "negative_ocf"
        
        ratio = (operating_cf_cr / revenue_cr) * 100
        return ratio, None
    
    @staticmethod
    def operating_cash_flow_to_net_income(operating_cf_cr: Optional[float],
                                         net_income_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """
        OCF to Net Income = Operating Cash Flow / Net Income
        Measures earnings quality - high ratio indicates sustainable earnings
        
        Ideal: > 1.0 (more cash than accounting profit)
        Red flag: < 0 or << 1 (earnings not backed by cash)
        """
        edge_case = None
        
        if operating_cf_cr is None or net_income_cr is None:
            return None, "missing_data"
        
        if net_income_cr == 0:
            return None, "zero_net_income"
        
        if net_income_cr < 0:
            return None, "negative_net_income"
        
        ratio = operating_cf_cr / net_income_cr
        return ratio, None
    
    @staticmethod
    def free_cash_flow(operating_cf_cr: Optional[float],
                      capex_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """
        Free Cash Flow = Operating Cash Flow - CapEx
        Available cash after maintaining/expanding asset base
        """
        edge_case = None
        
        if operating_cf_cr is None or capex_cr is None:
            return None, "missing_data"
        
        fcf = operating_cf_cr - capex_cr
        return fcf, None
    
    @staticmethod
    def capex_intensity(capex_cr: Optional[float],
                       revenue_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """
        CapEx Intensity = Capital Expenditure / Revenue
        Measures capital requirements for revenue generation
        
        High: Manufacturing, Infrastructure (15-30%)
        Low: Software, Services (2-10%)
        """
        edge_case = None
        
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
        """
        FCF Conversion = Free Cash Flow / Net Income
        Measures how much earnings convert to cash available for shareholders
        
        Ideal: > 0.8 (80%+ of profit converts to FCF)
        """
        edge_case = None
        
        if free_cash_flow_cr is None or net_income_cr is None:
            return None, "missing_data"
        
        if net_income_cr == 0:
            return None, "zero_net_income"
        
        if net_income_cr < 0:
            return None, "negative_net_income"
        
        conversion = free_cash_flow_cr / net_income_cr
        return conversion, None
    
    @staticmethod
    def cash_flow_from_operations_quality(operating_cf_cr: Optional[float],
                                         investing_cf_cr: Optional[float],
                                         financing_cf_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """
        CFO Quality = Operating CF / (Operating CF + Investing CF + Financing CF)
        Higher % of cash from operations indicates healthier business
        
        Good: > 60% from operations
        Warning: < 30% suggests reliance on investment/financing activities
        """
        edge_case = None
        
        if operating_cf_cr is None:
            return None, "missing_ocf"
        
        total_cf = (operating_cf_cr or 0) + (investing_cf_cr or 0) + (financing_cf_cr or 0)
        
        if total_cf == 0:
            return None, "zero_total_cf"
        
        quality = (operating_cf_cr / total_cf) * 100
        return quality, None


class CapitalAllocationClassifier:
    """
    Day 11: 8-pattern capital allocation classifier
    
    Analyzes cash deployment patterns to classify company strategy
    """
    
    @staticmethod
    def classify_capital_allocation(fcf_cr: Optional[float],
                                   capex_cr: Optional[float],
                                   dividend_paid_cr: Optional[float],
                                   debt_repayment_cr: Optional[float],
                                   net_income_cr: Optional[float],
                                   revenue_cr: Optional[float]) -> CapitalAllocationResult:
        """
        Classify capital allocation into 8 patterns
        
        Patterns:
        1. REINVESTMENT: High CapEx (>15% revenue), low dividend
        2. SHAREHOLDER_RETURNS: Low CapEx (<5% revenue), high dividend/buyback
        3. DELEVERAGING: FCF prioritized for debt reduction
        4. DEBT_ACCUMULATION: Negative FCF with increasing debt
        5. GROWTH_FOCUSED: All FCF into CapEx, minimal returns
        6. CONSERVATIVE: Accumulating cash, minimal deployment
        7. BALANCED: Balanced between growth, returns, debt reduction
        8. OPPORTUNISTIC: Unusual pattern (M&A, one-time events)
        """
        
        # Validate inputs
        if fcf_cr is None or capex_cr is None or net_income_cr is None or revenue_cr is None:
            return CapitalAllocationResult(
                pattern=CapitalAllocationPattern.OPPORTUNISTIC,
                confidence=0.0,
                reasoning="Insufficient data for classification",
                capex_intensity=0.0,
                fcf_conversion=0.0,
                dividend_payout_ratio=None
            )
        
        # Calculate metrics
        capex_intensity = (capex_cr / revenue_cr) * 100 if revenue_cr > 0 else 0
        fcf_conversion = fcf_cr / net_income_cr if net_income_cr > 0 else 0
        dividend_payout = (dividend_paid_cr / net_income_cr) * 100 if net_income_cr > 0 and dividend_paid_cr else None
        
        # Classification logic based on heuristics
        pattern, confidence, reasoning = CapitalAllocationClassifier._classify_pattern(
            fcf_cr, capex_cr, dividend_paid_cr, debt_repayment_cr,
            capex_intensity, fcf_conversion, dividend_payout
        )
        
        return CapitalAllocationResult(
            pattern=pattern,
            confidence=confidence,
            reasoning=reasoning,
            capex_intensity=capex_intensity,
            fcf_conversion=fcf_conversion,
            dividend_payout_ratio=dividend_payout
        )
    
    @staticmethod
    def _classify_pattern(fcf_cr: float, capex_cr: float, dividend_paid_cr: Optional[float],
                         debt_repayment_cr: Optional[float], capex_intensity: float,
                         fcf_conversion: float, dividend_payout: Optional[float]) -> Tuple[CapitalAllocationPattern, float, str]:
        """
        Internal classification logic
        Returns (pattern, confidence, reasoning)
        """
        
        dividend_paid = dividend_paid_cr or 0
        debt_repayment = debt_repayment_cr or 0
        
        # Pattern 1: REINVESTMENT - High CapEx, low/no dividend
        if capex_intensity > 15 and dividend_payout is None or dividend_payout < 10:
            return (CapitalAllocationPattern.REINVESTMENT, 0.85,
                   f"High CapEx intensity ({capex_intensity:.1f}%), minimal shareholder returns")
        
        # Pattern 2: SHAREHOLDER_RETURNS - Low CapEx, high dividend
        if capex_intensity < 5 and dividend_payout and dividend_payout > 30:
            return (CapitalAllocationPattern.SHAREHOLDER_RETURNS, 0.85,
                   f"Low CapEx ({capex_intensity:.1f}%), high dividend payout ({dividend_payout:.1f}%)")
        
        # Pattern 3: DELEVERAGING - FCF prioritized for debt reduction
        if fcf_cr > 0 and debt_repayment > fcf_cr * 0.5:
            return (CapitalAllocationPattern.DELEVERAGING, 0.80,
                   f"FCF prioritized for debt reduction ({debt_repayment:.1f}% of FCF)")
        
        # Pattern 4: DEBT_ACCUMULATION - Negative FCF with increasing debt
        if fcf_cr < 0 and debt_repayment < 0:  # debt_repayment negative means debt increase
            return (CapitalAllocationPattern.DEBT_ACCUMULATION, 0.80,
                   f"Negative FCF ({fcf_cr:.1f}) with debt accumulation")
        
        # Pattern 5: GROWTH_FOCUSED - All FCF into CapEx
        if fcf_cr > 0 and capex_cr > fcf_cr * 0.7 and (dividend_paid < fcf_cr * 0.1):
            return (CapitalAllocationPattern.GROWTH_FOCUSED, 0.80,
                   f"FCF deployed into CapEx ({capex_intensity:.1f}%), minimal shareholder returns")
        
        # Pattern 6: CONSERVATIVE - Accumulating cash
        if fcf_cr > 0 and dividend_paid < fcf_cr * 0.1 and debt_repayment < fcf_cr * 0.1:
            return (CapitalAllocationPattern.CONSERVATIVE, 0.75,
                   f"Positive FCF ({fcf_cr:.1f}) with minimal deployment")
        
        # Pattern 7: BALANCED - Balanced allocation
        if fcf_cr > 0:
            capex_share = capex_cr / fcf_cr if fcf_cr > 0 else 0
            dividend_share = dividend_paid / fcf_cr if fcf_cr > 0 else 0
            debt_share = debt_repayment / fcf_cr if fcf_cr > 0 else 0
            
            if 0.2 < capex_share < 0.6 and 0.1 < dividend_share < 0.4 and 0 < debt_share < 0.3:
                return (CapitalAllocationPattern.BALANCED, 0.80,
                       "Balanced allocation between CapEx, dividends, and debt reduction")
        
        # Pattern 8: OPPORTUNISTIC - Unusual pattern
        return (CapitalAllocationPattern.OPPORTUNISTIC, 0.60,
               "Capital allocation pattern does not fit standard categories")
