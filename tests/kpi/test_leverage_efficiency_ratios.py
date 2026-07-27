"""
Tests for Leverage & Efficiency Ratios (Day 09)
"""

import pytest
from src.analytics.ratios import LeverageRatios


class TestLeverageRatios:
    
    def test_de_normal_case(self):
        de, error = LeverageRatios.debt_to_equity(500, 1000)
        assert de == 0.5
        assert error is None
    
    def test_de_debt_free(self):
        de, error = LeverageRatios.debt_to_equity(0, 1000)
        assert de == 0.0
        assert error == "debt_free"
    
    def test_de_negative_equity(self):
        de, error = LeverageRatios.debt_to_equity(500, -1000)
        assert de is None
        assert error == "negative_equity"
    
    def test_de_zero_equity(self):
        de, error = LeverageRatios.debt_to_equity(500, 0)
        assert de is None
        assert error == "negative_equity"
    
    def test_de_missing_data(self):
        de, error = LeverageRatios.debt_to_equity(None, 1000)
        assert de is None
        assert error == "missing_data"
    
    def test_icr_normal_case(self):
        icr, error = LeverageRatios.interest_coverage_ratio(300, 30)
        assert icr == 10.0
        assert error is None
    
    def test_icr_debt_free(self):
        icr, error = LeverageRatios.interest_coverage_ratio(300, 0)
        assert icr is None
        assert error == "debt_free"
    
    def test_icr_negative_ebit(self):
        icr, error = LeverageRatios.interest_coverage_ratio(-300, 30)
        assert icr is None
        assert error == "insufficient_ebit"
    
    def test_icr_zero_ebit(self):
        icr, error = LeverageRatios.interest_coverage_ratio(0, 30)
        assert icr is None
        assert error == "insufficient_ebit"
    
    def test_asset_turnover_normal(self):
        at, error = LeverageRatios.asset_turnover(2000, 1000, 1200)
        assert at == pytest.approx(1.82, 0.01)
        assert error is None
    
    def test_asset_turnover_invalid_assets(self):
        at, error = LeverageRatios.asset_turnover(2000, 0, 1200)
        assert at is None
        assert error == "invalid_assets"
    
    def test_asset_turnover_missing_data(self):
        at, error = LeverageRatios.asset_turnover(None, 1000, 1200)
        assert at is None
        assert error == "missing_data"
    
    def test_net_debt_positive(self):
        nd, error = LeverageRatios.net_debt(500, 100)
        assert nd == 400
        assert error is None
    
    def test_net_debt_negative(self):
        nd, error = LeverageRatios.net_debt(500, 600)
        assert nd == -100
        assert error is None
