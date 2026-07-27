"""
Unit tests for Leverage & Efficiency Ratios (Day 09)
8 comprehensive tests covering D/E, ICR, Asset Turnover, Net Debt with edge cases
"""

import pytest
from src.analytics.ratios import LeverageRatios, EfficiencyRatios


class TestDebtToEquity:
    """D/E Ratio tests"""
    
    def test_de_normal_case(self):
        """Test D/E calculation with normal values"""
        de, edge_case = LeverageRatios.debt_to_equity(
            total_debt_cr=500,
            equity_cr=1000
        )
        assert de == pytest.approx(0.5)
        assert edge_case is None
    
    def test_de_debt_free_company(self):
        """Test D/E with debt-free company (zero debt)"""
        de, edge_case = LeverageRatios.debt_to_equity(
            total_debt_cr=0,
            equity_cr=1000
        )
        assert de == 0.0
        assert edge_case is not None
        assert edge_case.edge_case == "debt_free"
    
    def test_de_negative_equity(self):
        """Test D/E with negative equity"""
        de, edge_case = LeverageRatios.debt_to_equity(
            total_debt_cr=500,
            equity_cr=-1000
        )
        assert de is None
        assert edge_case is not None
        assert edge_case.edge_case == "negative_equity"


class TestInterestCoverageRatio:
    """ICR tests"""
    
    def test_icr_normal_case(self):
        """Test ICR calculation with normal values"""
        icr, edge_case = LeverageRatios.interest_coverage_ratio(
            ebit_cr=200,
            interest_expense_cr=50
        )
        assert icr == pytest.approx(4.0)
        assert edge_case is None
    
    def test_icr_debt_free_company(self):
        """Test ICR with debt-free company (zero interest)"""
        icr, edge_case = LeverageRatios.interest_coverage_ratio(
            ebit_cr=200,
            interest_expense_cr=0
        )
        assert icr is None
        assert edge_case is not None
        assert edge_case.edge_case == "debt_free"
    
    def test_icr_insufficient_ebit(self):
        """Test ICR with zero EBIT"""
        icr, edge_case = LeverageRatios.interest_coverage_ratio(
            ebit_cr=0,
            interest_expense_cr=50
        )
        assert icr is None
        assert edge_case is not None
        assert edge_case.edge_case == "insufficient_ebit"
    
    def test_icr_negative_interest(self):
        """Test ICR with negative interest expense"""
        icr, edge_case = LeverageRatios.interest_coverage_ratio(
            ebit_cr=200,
            interest_expense_cr=-50
        )
        assert icr is None
        assert edge_case is not None
        assert edge_case.edge_case == "negative_interest"


class TestAssetTurnover:
    """Asset Turnover tests"""
    
    def test_asset_turnover_normal_case(self):
        """Test Asset Turnover calculation with normal values"""
        at, edge_case = LeverageRatios.asset_turnover(
            revenue_cr=1000,
            beginning_assets_cr=2000,
            ending_assets_cr=2500
        )
        assert at == pytest.approx(0.4444444, rel=1e-6)
        assert edge_case is None
    
    def test_asset_turnover_zero_average_assets(self):
        """Test Asset Turnover with zero average assets"""
        at, edge_case = LeverageRatios.asset_turnover(
            revenue_cr=1000,
            beginning_assets_cr=0,
            ending_assets_cr=0
        )
        assert at is None
        assert edge_case is not None
        # invalid_assets is caught first in the validation
        assert edge_case.edge_case in ["invalid_assets", "zero_average_assets"]


class TestNetDebt:
    """Net Debt tests"""
    
    def test_net_debt_positive_debt(self):
        """Test Net Debt with positive debt position"""
        nd, edge_case = LeverageRatios.net_debt(
            total_debt_cr=500,
            cash_and_equivalents_cr=100
        )
        assert nd == 400
        assert edge_case is None
    
    def test_net_debt_net_cash_position(self):
        """Test Net Debt with net cash position (negative net debt)"""
        nd, edge_case = LeverageRatios.net_debt(
            total_debt_cr=100,
            cash_and_equivalents_cr=500
        )
        assert nd == -400
        assert edge_case is None


class TestWorkingCapitalTurnover:
    """Working Capital Turnover tests"""
    
    def test_wc_turnover_normal_case(self):
        """Test WC Turnover with normal values"""
        wc, edge_case = EfficiencyRatios.working_capital_turnover(
            revenue_cr=1000,
            current_assets_cr=600,
            current_liabilities_cr=200
        )
        assert wc == pytest.approx(2.5)
        assert edge_case is None
    
    def test_wc_turnover_negative_wc(self):
        """Test WC Turnover with negative working capital"""
        wc, edge_case = EfficiencyRatios.working_capital_turnover(
            revenue_cr=1000,
            current_assets_cr=100,
            current_liabilities_cr=200
        )
        assert wc is None
        assert edge_case is not None
        assert edge_case.edge_case == "negative_working_capital"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
