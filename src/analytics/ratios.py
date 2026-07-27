"""
N100 Financial Ratio Engine - Profitability, Leverage, Efficiency Ratios
Day 08-09: Core ratio calculations with edge case handling
"""

import logging
from typing import Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RatioEdgeCase:
    """Edge case metadata for ratio calculations"""
    ratio_name: str
    edge_case: str
    value: Optional[float] = None
    company_id: str = ""
    year: int = 0


class ProfitabilityRatios:
    """Day 08: Profitability ratios"""
    
    @staticmethod
    def net_profit_margin(net_profit_cr: Optional[float], 
                         revenue_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """Net Profit Margin = (Net Profit / Revenue) * 100"""
        if net_profit_cr is None or revenue_cr is None:
            return None, "missing_data"
        
        if revenue_cr == 0:
            return None, "zero_revenue"
        
        npm = (net_profit_cr / revenue_cr) * 100
        return npm, None
    
    @staticmethod
    def operating_profit_margin(operating_profit_cr: Optional[float],
                               revenue_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """Operating Profit Margin = (Operating Profit / Revenue) * 100"""
        if operating_profit_cr is None or revenue_cr is None:
            return None, "missing_data"
        
        if revenue_cr == 0:
            return None, "zero_revenue"
        
        opm = (operating_profit_cr / revenue_cr) * 100
        return opm, None
    
    @staticmethod
    def return_on_equity(net_profit_cr: Optional[float],
                        beginning_equity_cr: Optional[float],
                        ending_equity_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """ROE = (Net Profit / Average Equity) * 100"""
        if net_profit_cr is None or beginning_equity_cr is None or ending_equity_cr is None:
            return None, "missing_data"
        
        if beginning_equity_cr < 0 or ending_equity_cr < 0:
            return None, "negative_equity"
        
        avg_equity = (beginning_equity_cr + ending_equity_cr) / 2
        
        if avg_equity <= 0:
            return None, "negative_average_equity"
        
        roe = (net_profit_cr / avg_equity) * 100
        return roe, None
    
    @staticmethod
    def return_on_capital_employed(ebit_cr: Optional[float],
                                   equity_cr: Optional[float],
                                   total_debt_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """ROCE = (EBIT / Capital Employed) * 100"""
        if ebit_cr is None or equity_cr is None or total_debt_cr is None:
            return None, "missing_data"
        
        if equity_cr < 0:
            return None, "negative_equity"
        
        capital_employed = equity_cr + total_debt_cr
        
        if capital_employed <= 0:
            return None, "zero_capital_employed"
        
        roce = (ebit_cr / capital_employed) * 100
        return roce, None
    
    @staticmethod
    def return_on_assets(net_profit_cr: Optional[float],
                        beginning_assets_cr: Optional[float],
                        ending_assets_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """ROA = (Net Profit / Average Total Assets) * 100"""
        if net_profit_cr is None or beginning_assets_cr is None or ending_assets_cr is None:
            return None, "missing_data"
        
        if beginning_assets_cr <= 0 or ending_assets_cr <= 0:
            return None, "invalid_assets"
        
        avg_assets = (beginning_assets_cr + ending_assets_cr) / 2
        
        if avg_assets <= 0:
            return None, "zero_average_assets"
        
        roa = (net_profit_cr / avg_assets) * 100
        return roa, None


class LeverageRatios:
    """Day 09: Leverage & Solvency ratios"""
    
    @staticmethod
    def debt_to_equity(total_debt_cr: Optional[float],
                      equity_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """D/E = Total Debt / Equity (returns 0 for debt-free, not None)"""
        if total_debt_cr is None or equity_cr is None:
            return None, "missing_data"
        
        if total_debt_cr == 0:
            return 0.0, "debt_free"
        
        if equity_cr <= 0:
            return None, "negative_equity"
        
        de_ratio = total_debt_cr / equity_cr
        return de_ratio, None
    
    @staticmethod
    def interest_coverage_ratio(ebit_cr: Optional[float],
                               interest_expense_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """ICR = EBIT / Interest Expense"""
        if ebit_cr is None or interest_expense_cr is None:
            return None, "missing_data"
        
        if interest_expense_cr == 0:
            return None, "debt_free"
        
        if interest_expense_cr < 0:
            return None, "negative_interest"
        
        if ebit_cr <= 0:
            return None, "insufficient_ebit"
        
        icr = ebit_cr / interest_expense_cr
        return icr, None
    
    @staticmethod
    def asset_turnover(revenue_cr: Optional[float],
                      beginning_assets_cr: Optional[float],
                      ending_assets_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """Asset Turnover = Revenue / Average Total Assets"""
        if revenue_cr is None or beginning_assets_cr is None or ending_assets_cr is None:
            return None, "missing_data"
        
        if beginning_assets_cr <= 0 or ending_assets_cr <= 0:
            return None, "invalid_assets"
        
        avg_assets = (beginning_assets_cr + ending_assets_cr) / 2
        
        if avg_assets <= 0:
            return None, "zero_average_assets"
        
        asset_turnover = revenue_cr / avg_assets
        return asset_turnover, None
    
    @staticmethod
    def net_debt(total_debt_cr: Optional[float],
                cash_and_equivalents_cr: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
        """Net Debt = Total Debt - Cash & Equivalents"""
        if total_debt_cr is None or cash_and_equivalents_cr is None:
            return None, "missing_data"
        
        net_debt = total_debt_cr - cash_and_equivalents_cr
        return net_debt, None


def calculate_ebit(net_profit_cr: Optional[float],
                   interest_expense_cr: Optional[float],
                   tax_expense_cr: Optional[float]) -> Optional[float]:
    """EBIT = Net Profit + Interest Expense + Tax Expense"""
    if net_profit_cr is None or interest_expense_cr is None or tax_expense_cr is None:
        return None
    
    ebit = net_profit_cr + interest_expense_cr + tax_expense_cr
    return ebit


def calculate_total_debt(long_term_debt_cr: Optional[float],
                        short_term_borrowings_cr: Optional[float]) -> Optional[float]:
    """Total Debt = Long-term Debt + Short-term Borrowings"""
    if long_term_debt_cr is None or short_term_borrowings_cr is None:
        return None
    
    total_debt = long_term_debt_cr + short_term_borrowings_cr
    return total_debt
