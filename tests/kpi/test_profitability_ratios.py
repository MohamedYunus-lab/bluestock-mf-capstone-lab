"""
Tests for Profitability Ratios (Day 08)
"""

import pytest
from src.analytics.ratios import ProfitabilityRatios, calculate_ebit


class TestProfitabilityRatios:
    
    def test_npm_normal_case(self):
        npm, error = ProfitabilityRatios.net_profit_margin(100, 1000)
        assert npm == 10.0
        assert error is None
    
    def test_npm_zero_revenue(self):
        npm, error = ProfitabilityRatios.net_profit_margin(100, 0)
        assert npm is None
        assert error == "zero_revenue"
    
    def test_npm_missing_data(self):
        npm, error = ProfitabilityRatios.net_profit_margin(None, 1000)
        assert npm is None
        assert error == "missing_data"
    
    def test_opm_normal_case(self):
        opm, error = ProfitabilityRatios.operating_profit_margin(200, 1000)
        assert opm == 20.0
        assert error is None
    
    def test_opm_zero_revenue(self):
        opm, error = ProfitabilityRatios.operating_profit_margin(200, 0)
        assert opm is None
        assert error == "zero_revenue"
    
    def test_roe_normal_case(self):
        roe, error = ProfitabilityRatios.return_on_equity(100, 500, 600)
        assert roe == pytest.approx(18.18, 0.1)
        assert error is None
    
    def test_roe_negative_equity(self):
        roe, error = ProfitabilityRatios.return_on_equity(100, -500, 600)
        assert roe is None
        assert error == "negative_equity"
    
    def test_roe_zero_average_equity(self):
        roe, error = ProfitabilityRatios.return_on_equity(100, -500, 500)
        assert roe is None
        assert error == "negative_equity"
    
    def test_roce_normal_case(self):
        roce, error = ProfitabilityRatios.return_on_capital_employed(300, 500, 200)
        assert roce == pytest.approx(42.86, 0.1)
        assert error is None
    
    def test_roce_negative_equity(self):
        roce, error = ProfitabilityRatios.return_on_capital_employed(300, -500, 200)
        assert roce is None
        assert error == "negative_equity"
    
    def test_roce_zero_capital_employed(self):
        roce, error = ProfitabilityRatios.return_on_capital_employed(300, -100, 100)
        assert roce is None
        assert error == "negative_equity"
    
    def test_roa_normal_case(self):
        roa, error = ProfitabilityRatios.return_on_assets(150, 1000, 1200)
        assert roa == pytest.approx(12.82, 0.1)
        assert error is None
    
    def test_roa_invalid_assets(self):
        roa, error = ProfitabilityRatios.return_on_assets(150, 0, 1200)
        assert roa is None
        assert error == "invalid_assets"
    
    def test_roa_missing_data(self):
        roa, error = ProfitabilityRatios.return_on_assets(None, 1000, 1200)
        assert roa is None
        assert error == "missing_data"
    
    def test_calculate_ebit_normal(self):
        ebit = calculate_ebit(100, 20, 30)
        assert ebit == 150
    
    def test_calculate_ebit_missing_data(self):
        ebit = calculate_ebit(100, None, 30)
        assert ebit is None
