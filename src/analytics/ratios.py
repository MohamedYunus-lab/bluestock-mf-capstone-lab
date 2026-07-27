"""
N100 Financial Ratio Engine - Profitability & Leverage & Efficiency Ratios
Day 08-09: Core ratio calculations with edge case handling
"""

import logging
from typing import Optional, Dict, Tuple
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
    """
    Day 08: Profitability ratios
    - NPM (Net Profit Margin) = Net Profit / Revenue
    - OPM (Operating Profit Margin) = Operating Profit / Revenue
    - ROE (Return on Equity) = Net Profit / Average Equity
    - ROCE (Return on Capital Employed) = EBIT / Capital Employed
    - ROA (Return on Assets) = Net Profit / Average Total Assets
    """
    
    @staticmethod
    def net_profit_margin(net_profit_cr: Optional[float], 
                         revenue_cr: Optional[float]) -> Tuple[Optional[float], Optional[RatioEdgeCase]]:
        """
        Net Profit Margin = (Net Profit / Revenue) * 100
        
        Returns:
            (npm_value, edge_case_obj or None)
        """
        edge_case = None
        
        if net_profit_cr is None or revenue_cr is None:
            edge_case = RatioEdgeCase("NPM", "missing_data")
            return None, edge_case
        
        if revenue_cr == 0:
            edge_case = RatioEdgeCase("NPM", "zero_revenue")
            return None, edge_case
        
        npm = (net_profit_cr / revenue_cr) * 100
        return npm, None
    
    @staticmethod
    def operating_profit_margin(operating_profit_cr: Optional[float],
                               revenue_cr: Optional[float]) -> Tuple[Optional[float], Optional[RatioEdgeCase]]:
        """
        Operating Profit Margin = (Operating Profit / Revenue) * 100
        """
        edge_case = None
        
        if operating_profit_cr is None or revenue_cr is None:
            edge_case = RatioEdgeCase("OPM", "missing_data")
            return None, edge_case
        
        if revenue_cr == 0:
            edge_case = RatioEdgeCase("OPM", "zero_revenue")
            return None, edge_case
        
        opm = (operating_profit_cr / revenue_cr) * 100
        return opm, None
    
    @staticmethod
    def return_on_equity(net_profit_cr: Optional[float],
                        beginning_equity_cr: Optional[float],
                        ending_equity_cr: Optional[float]) -> Tuple[Optional[float], Optional[RatioEdgeCase]]:
        """
        ROE = (Net Profit / Average Equity) * 100
        Average Equity = (Beginning Equity + Ending Equity) / 2
        
        Edge cases:
        - Negative equity → return None with edge_case
        - Zero/negative average equity → return None with edge_case
        """
        edge_case = None
        
        if net_profit_cr is None:
            edge_case = RatioEdgeCase("ROE", "missing_net_profit")
            return None, edge_case
        
        if beginning_equity_cr is None or ending_equity_cr is None:
            edge_case = RatioEdgeCase("ROE", "missing_equity")
            return None, edge_case
        
        if beginning_equity_cr < 0 or ending_equity_cr < 0:
            edge_case = RatioEdgeCase("ROE", "negative_equity")
            return None, edge_case
        
        avg_equity = (beginning_equity_cr + ending_equity_cr) / 2
        
        if avg_equity <= 0:
            edge_case = RatioEdgeCase("ROE", "negative_average_equity")
            return None, edge_case
        
        roe = (net_profit_cr / avg_equity) * 100
        return roe, None
    
    @staticmethod
    def return_on_capital_employed(ebit_cr: Optional[float],
                                   equity_cr: Optional[float],
                                   long_term_debt_cr: Optional[float]) -> Tuple[Optional[float], Optional[RatioEdgeCase]]:
        """
        ROCE = (EBIT / Capital Employed) * 100
        Capital Employed = Equity + Long-term Debt
        EBIT = Operating Profit (or PBIT)
        
        Note: EBIT calculation: Net Profit + Interest Expense + Tax Expense
        """
        edge_case = None
        
        if ebit_cr is None:
            edge_case = RatioEdgeCase("ROCE", "missing_ebit")
            return None, edge_case
        
        if equity_cr is None or long_term_debt_cr is None:
            edge_case = RatioEdgeCase("ROCE", "missing_capital")
            return None, edge_case
        
        if equity_cr < 0:
            edge_case = RatioEdgeCase("ROCE", "negative_equity")
            return None, edge_case
        
        capital_employed = equity_cr + long_term_debt_cr
        
        if capital_employed <= 0:
            edge_case = RatioEdgeCase("ROCE", "zero_capital_employed")
            return None, edge_case
        
        roce = (ebit_cr / capital_employed) * 100
        return roce, None
    
    @staticmethod
    def return_on_assets(net_profit_cr: Optional[float],
                        beginning_assets_cr: Optional[float],
                        ending_assets_cr: Optional[float]) -> Tuple[Optional[float], Optional[RatioEdgeCase]]:
        """
        ROA = (Net Profit / Average Total Assets) * 100
        Average Total Assets = (Beginning Assets + Ending Assets) / 2
        """
        edge_case = None
        
        if net_profit_cr is None:
            edge_case = RatioEdgeCase("ROA", "missing_net_profit")
            return None, edge_case
        
        if beginning_assets_cr is None or ending_assets_cr is None:
            edge_case = RatioEdgeCase("ROA", "missing_assets")
            return None, edge_case
        
        if beginning_assets_cr <= 0 or ending_assets_cr <= 0:
            edge_case = RatioEdgeCase("ROA", "invalid_assets")
            return None, edge_case
        
        avg_assets = (beginning_assets_cr + ending_assets_cr) / 2
        
        if avg_assets <= 0:
            edge_case = RatioEdgeCase("ROA", "zero_average_assets")
            return None, edge_case
        
        roa = (net_profit_cr / avg_assets) * 100
        return roa, None


class LeverageRatios:
    """
    Day 09: Leverage & Solvency ratios
    - D/E (Debt-to-Equity) = Total Debt / Equity
    - ICR (Interest Coverage Ratio) = EBIT / Interest Expense
    - Asset Turnover = Revenue / Average Total Assets
    - Net Debt = Total Debt - Cash & Equivalents
    """
    
    @staticmethod
    def debt_to_equity(total_debt_cr: Optional[float],
                      equity_cr: Optional[float]) -> Tuple[Optional[float], Optional[RatioEdgeCase]]:
        """
        D/E = Total Debt / Equity
        
        Edge cases:
        - Debt-free (total_debt = 0) → return 0 with label 'debt_free'
        - Negative equity → return None
        - Zero/negative equity → return None
        """
        edge_case = None
        
        if total_debt_cr is None or equity_cr is None:
            edge_case = RatioEdgeCase("D/E", "missing_data")
            return None, edge_case
        
        if total_debt_cr == 0:
            # Debt-free company: D/E = 0, not None
            edge_case = RatioEdgeCase("D/E", "debt_free", 0.0)
            return 0.0, edge_case
        
        if equity_cr <= 0:
            edge_case = RatioEdgeCase("D/E", "negative_equity")
            return None, edge_case
        
        de_ratio = total_debt_cr / equity_cr
        return de_ratio, None
    
    @staticmethod
    def interest_coverage_ratio(ebit_cr: Optional[float],
                               interest_expense_cr: Optional[float]) -> Tuple[Optional[float], Optional[RatioEdgeCase]]:
        """
        ICR = EBIT / Interest Expense
        
        Edge cases:
        - Interest expense = 0 (debt-free) → return None with label 'debt_free'
        - Interest expense < 0 → return None
        - Zero/negative EBIT → return None with label 'insufficient_ebit'
        """
        edge_case = None
        
        if ebit_cr is None or interest_expense_cr is None:
            edge_case = RatioEdgeCase("ICR", "missing_data")
            return None, edge_case
        
        if interest_expense_cr == 0:
            edge_case = RatioEdgeCase("ICR", "debt_free")
            return None, edge_case
        
        if interest_expense_cr < 0:
            edge_case = RatioEdgeCase("ICR", "negative_interest")
            return None, edge_case
        
        if ebit_cr <= 0:
            edge_case = RatioEdgeCase("ICR", "insufficient_ebit")
            return None, edge_case
        
        icr = ebit_cr / interest_expense_cr
        return icr, None
    
    @staticmethod
    def asset_turnover(revenue_cr: Optional[float],
                      beginning_assets_cr: Optional[float],
                      ending_assets_cr: Optional[float]) -> Tuple[Optional[float], Optional[RatioEdgeCase]]:
        """
        Asset Turnover = Revenue / Average Total Assets
        """
        edge_case = None
        
        if revenue_cr is None:
            edge_case = RatioEdgeCase("Asset_Turnover", "missing_revenue")
            return None, edge_case
        
        if beginning_assets_cr is None or ending_assets_cr is None:
            edge_case = RatioEdgeCase("Asset_Turnover", "missing_assets")
            return None, edge_case
        
        if beginning_assets_cr <= 0 or ending_assets_cr <= 0:
            edge_case = RatioEdgeCase("Asset_Turnover", "invalid_assets")
            return None, edge_case
        
        avg_assets = (beginning_assets_cr + ending_assets_cr) / 2
        
        if avg_assets <= 0:
            edge_case = RatioEdgeCase("Asset_Turnover", "zero_average_assets")
            return None, edge_case
        
        asset_turnover = revenue_cr / avg_assets
        return asset_turnover, None
    
    @staticmethod
    def net_debt(total_debt_cr: Optional[float],
                cash_and_equivalents_cr: Optional[float]) -> Tuple[Optional[float], Optional[RatioEdgeCase]]:
        """
        Net Debt = Total Debt - Cash & Equivalents
        Can be negative (net cash position) or positive (net debt position)
        """
        edge_case = None
        
        if total_debt_cr is None or cash_and_equivalents_cr is None:
            edge_case = RatioEdgeCase("Net_Debt", "missing_data")
            return None, edge_case
        
        net_debt = total_debt_cr - cash_and_equivalents_cr
        return net_debt, None


class EfficiencyRatios:
    """
    Day 09: Efficiency ratios derived from leverage/profitability
    - Working Capital Turnover
    - Days Sales Outstanding (DSO)
    - Days Inventory Outstanding (DIO)
    """
    
    @staticmethod
    def working_capital_turnover(revenue_cr: Optional[float],
                                current_assets_cr: Optional[float],
                                current_liabilities_cr: Optional[float]) -> Tuple[Optional[float], Optional[RatioEdgeCase]]:
        """
        Working Capital Turnover = Revenue / (Current Assets - Current Liabilities)
        """
        edge_case = None
        
        if revenue_cr is None:
            edge_case = RatioEdgeCase("WC_Turnover", "missing_revenue")
            return None, edge_case
        
        if current_assets_cr is None or current_liabilities_cr is None:
            edge_case = RatioEdgeCase("WC_Turnover", "missing_data")
            return None, edge_case
        
        working_capital = current_assets_cr - current_liabilities_cr
        
        if working_capital <= 0:
            edge_case = RatioEdgeCase("WC_Turnover", "negative_working_capital")
            return None, edge_case
        
        wc_turnover = revenue_cr / working_capital
        return wc_turnover, None
    
    @staticmethod
    def days_sales_outstanding(receivables_cr: Optional[float],
                              revenue_cr: Optional[float]) -> Tuple[Optional[float], Optional[RatioEdgeCase]]:
        """
        DSO = (Receivables / Revenue) * 365
        """
        edge_case = None
        
        if receivables_cr is None or revenue_cr is None:
            edge_case = RatioEdgeCase("DSO", "missing_data")
            return None, edge_case
        
        if revenue_cr == 0:
            edge_case = RatioEdgeCase("DSO", "zero_revenue")
            return None, edge_case
        
        dso = (receivables_cr / revenue_cr) * 365
        return dso, None
    
    @staticmethod
    def days_inventory_outstanding(inventory_cr: Optional[float],
                                  revenue_cr: Optional[float]) -> Tuple[Optional[float], Optional[RatioEdgeCase]]:
        """
        DIO = (Inventory / Revenue) * 365
        """
        edge_case = None
        
        if inventory_cr is None or revenue_cr is None:
            edge_case = RatioEdgeCase("DIO", "missing_data")
            return None, edge_case
        
        if revenue_cr == 0:
            edge_case = RatioEdgeCase("DIO", "zero_revenue")
            return None, edge_case
        
        dio = (inventory_cr / revenue_cr) * 365
        return dio, None


def calculate_ebit(net_profit_cr: Optional[float],
                   interest_expense_cr: Optional[float],
                   tax_expense_cr: Optional[float]) -> Optional[float]:
    """
    Helper: Calculate EBIT from Net Profit
    EBIT = Net Profit + Interest Expense + Tax Expense
    """
    if net_profit_cr is None or interest_expense_cr is None or tax_expense_cr is None:
        return None
    
    ebit = net_profit_cr + interest_expense_cr + tax_expense_cr
    return ebit if ebit > 0 or ebit == 0 else None


def calculate_total_debt(long_term_debt_cr: Optional[float],
                        short_term_borrowings_cr: Optional[float]) -> Optional[float]:
    """
    Helper: Calculate Total Debt
    Total Debt = Long-term Debt + Short-term Borrowings
    """
    if long_term_debt_cr is None or short_term_borrowings_cr is None:
        return None
    
    total_debt = long_term_debt_cr + short_term_borrowings_cr
    return total_debt
