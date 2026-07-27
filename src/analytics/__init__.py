"""Analytics module for N100 Financial Ratio Engine"""

from .ratios import (
    ProfitabilityRatios,
    LeverageRatios,
    EfficiencyRatios,
    RatioEdgeCase,
    calculate_ebit,
    calculate_total_debt
)

from .cagr import (
    CAGREngine,
    CAGREdgeCase
)

from .cashflow_kpis import (
    CashflowQualityMetrics,
    CapitalAllocationClassifier,
    CapitalAllocationPattern,
    CapitalAllocationResult,
    CashflowMetric
)

__all__ = [
    'ProfitabilityRatios',
    'LeverageRatios',
    'EfficiencyRatios',
    'RatioEdgeCase',
    'calculate_ebit',
    'calculate_total_debt',
    'CAGREngine',
    'CAGREdgeCase',
    'CashflowQualityMetrics',
    'CapitalAllocationClassifier',
    'CapitalAllocationPattern',
    'CapitalAllocationResult',
    'CashflowMetric'
]
