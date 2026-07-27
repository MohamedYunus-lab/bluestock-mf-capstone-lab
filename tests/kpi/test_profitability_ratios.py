"""
Unit tests for Profitability Ratios (Day 08)
8 comprehensive tests covering NPM, OPM, ROE, ROCE, ROA with edge cases
"""

import pytest
from src.analytics.ratios import ProfitabilityRatios, calculate_ebit


class TestNetProfitMargin:
    """NPM tests"""
    
    def test_npm_normal_case(self):
        """Test NPM calculation with normal positive values"""
        npm, edge_case = ProfitabilityRatios.net_profit_margin(
            net_profit_cr=100,
            revenue_cr=1000
        )
        assert npm == pytest.approx(10.0)
        assert edge_case is None
    
    def test_npm_zero_revenue(self):
        """Test NPM with zero revenue (edge case)"""
        npm, edge_case = ProfitabilityRatios.net_profit_margin(
            net_profit_cr=100,
            revenue_cr=0
        )
        assert npm is None
        assert edge_case is not None
        assert edge_case.edge_case == "zero_revenue"
    
    def test_npm_missing_data(self):
        """Test NPM with missing profit data"""
        npm, edge_case = ProfitabilityRatios.net_profit_margin(
            net_profit_cr=None,
            revenue_cr=1000
        )
        assert npm is None
        assert edge_case is not None
        assert edge_case.edge_case == "missing_data"


class TestOperatingProfitMargin:
    """OPM tests"""
    
    def test_opm_normal_case(self):
        """Test OPM calculation with normal values"""
        opm, edge_case = ProfitabilityRatios.operating_profit_margin(
            operating_profit_cr=200,
            revenue_cr=1000
        )
        assert opm == pytest.approx(20.0)
        assert edge_case is None
    
    def test_opm_zero_revenue(self):
        """Test OPM with zero revenue"""
        opm, edge_case = ProfitabilityRatios.operating_profit_margin(
            operating_profit_cr=200,
            revenue_cr=0
        )
        assert opm is None
        assert edge_case is not None
        assert edge_case.edge_case == "zero_revenue"


class TestReturnOnEquity:
    """ROE tests"""
    
    def test_roe_normal_case(self):
        """Test ROE calculation with normal equity"""
        roe, edge_case = ProfitabilityRatios.return_on_equity(
            net_profit_cr=100,
            beginning_equity_cr=1000,
            ending_equity_cr=1100
        )
        assert roe == pytest.approx(9.52380952, rel=1e-6)
        assert edge_case is None
    
    def test_roe_negative_equity(self):
        """Test ROE with negative equity (edge case)"""
        roe, edge_case = ProfitabilityRatios.return_on_equity(
            net_profit_cr=100,
            beginning_equity_cr=-1000,
            ending_equity_cr=1100
        )
        assert roe is None
        assert edge_case is not None
        assert edge_case.edge_case == "negative_equity"
    
    def test_roe_zero_average_equity(self):
        """Test ROE with zero average equity"""
        roe, edge_case = ProfitabilityRatios.return_on_equity(
            net_profit_cr=100,
            beginning_equity_cr=-1000,
            ending_equity_cr=1000
        )
        assert roe is None
        assert edge_case is not None
        # Should catch negative_equity first in the check
        assert edge_case.edge_case in ["negative_equity", "negative_average_equity"]


class TestReturnOnCapitalEmployed:
    """ROCE tests"""
    
    def test_roce_normal_case(self):
        """Test ROCE calculation with normal values"""
        roce, edge_case = ProfitabilityRatios.return_on_capital_employed(
            ebit_cr=200,
            equity_cr=1000,
            long_term_debt_cr=500
        )
        assert roce == pytest.approx(13.333333, rel=1e-6)
        assert edge_case is None
    
    def test_roce_negative_equity(self):
        """Test ROCE with negative equity"""
        roce, edge_case = ProfitabilityRatios.return_on_capital_employed(
            ebit_cr=200,
            equity_cr=-500,
            long_term_debt_cr=500
        )
        assert roce is None
        assert edge_case is not None
        assert edge_case.edge_case == "negative_equity"
    
    def test_roce_zero_capital_employed(self):
        """Test ROCE with zero capital employed"""
        roce, edge_case = ProfitabilityRatios.return_on_capital_employed(
            ebit_cr=200,
            equity_cr=0,
            long_term_debt_cr=0
        )
        assert roce is None
        assert edge_case is not None
        assert edge_case.edge_case == "zero_capital_employed"


class TestReturnOnAssets:
    """ROA tests"""
    
    def test_roa_normal_case(self):
        """Test ROA calculation with normal values"""
        roa, edge_case = ProfitabilityRatios.return_on_assets(
            net_profit_cr=100,
            beginning_assets_cr=1000,
            ending_assets_cr=1200
        )
        # Average assets = (1000 + 1200) / 2 = 1100
        # ROA = (100 / 1100) * 100 = 9.0909%
        assert roa == pytest.approx(9.090909, rel=1e-6)
        assert edge_case is None
    
    def test_roa_invalid_assets(self):
        """Test ROA with invalid assets"""
        roa, edge_case = ProfitabilityRatios.return_on_assets(
            net_profit_cr=100,
            beginning_assets_cr=0,
            ending_assets_cr=1200
        )
        assert roa is None
        assert edge_case is not None
        assert edge_case.edge_case == "invalid_assets"


class TestEBITCalculation:
    """Helper function: EBIT calculation"""
    
    def test_ebit_normal(self):
        """Test EBIT calculation from net profit"""
        ebit = calculate_ebit(
            net_profit_cr=100,
            interest_expense_cr=50,
            tax_expense_cr=20
        )
        assert ebit == 170
    
    def test_ebit_missing_data(self):
        """Test EBIT with missing tax data"""
        ebit = calculate_ebit(
            net_profit_cr=100,
            interest_expense_cr=50,
            tax_expense_cr=None
        )
        assert ebit is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
