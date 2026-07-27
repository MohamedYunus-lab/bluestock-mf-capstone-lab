"""
Tests for CAGR Engine (Day 10)
"""

import pytest
from src.analytics.cagr import CAGREngine


class TestCAGREngine:
    
    def test_calculate_cagr_normal(self):
        cagr, ec = CAGREngine.calculate_cagr(100, 133.1, 3)
        assert cagr == pytest.approx(10.0, 0.1)
        assert ec is None
    
    def test_calculate_cagr_turnaround(self):
        cagr, ec = CAGREngine.calculate_cagr(-100, 200, 3)
        assert cagr is None
        assert ec.flag == "TURNAROUND"
    
    def test_calculate_cagr_decline(self):
        cagr, ec = CAGREngine.calculate_cagr(100, -50, 3)
        assert cagr is None
        assert ec.flag == "DECLINE"
    
    def test_calculate_cagr_both_negative(self):
        cagr, ec = CAGREngine.calculate_cagr(-100, -50, 3)
        assert cagr is None
        assert ec.flag == "BOTH_NEGATIVE"
    
    def test_calculate_cagr_zero_base(self):
        cagr, ec = CAGREngine.calculate_cagr(0, 100, 3)
        assert cagr is None
        assert ec.flag == "ZERO_BASE"
    
    def test_revenue_cagr_normal(self):
        series = {2019: 1000, 2020: 1100, 2021: 1210, 2022: 1331, 2023: 1464}
        cagr, ec = CAGREngine.calculate_revenue_cagr(series, num_years=3)
        assert cagr == pytest.approx(10.0, 0.1)
        assert ec is None
    
    def test_revenue_cagr_insufficient_data(self):
        series = {2021: 1000, 2022: 1100}
        cagr, ec = CAGREngine.calculate_revenue_cagr(series, num_years=3)
        assert cagr is None
        assert ec.flag == "INSUFFICIENT_DATA"
    
    def test_revenue_cagr_missing_data(self):
        series = {2019: 1000, 2020: None, 2021: 1210, 2022: 1331, 2023: 1464}
        cagr, ec = CAGREngine.calculate_revenue_cagr(series, num_years=3)
        assert cagr is None
        assert ec.flag == "MISSING_DATA"
    
    def test_pat_cagr_normal(self):
        series = {2019: 100, 2020: 110, 2021: 121, 2022: 133, 2023: 146}
        cagr, ec = CAGREngine.calculate_pat_cagr(series, num_years=3)
        assert cagr == pytest.approx(10.0, 0.1)
        assert ec is None
    
    def test_eps_cagr_turnaround(self):
        series = {2019: 5, 2020: 10, 2021: 15, 2022: -10, 2023: -20}
        cagr, ec = CAGREngine.calculate_eps_cagr(series, num_years=3)
        assert cagr is None
        assert ec.flag == "DECLINE"
    
    def test_calculate_cagr_5_year(self):
        cagr, ec = CAGREngine.calculate_cagr(100, 161.05, 5)
        assert cagr == pytest.approx(10.0, 0.1)
        assert ec is None
    
    def test_calculate_cagr_10_year(self):
        cagr, ec = CAGREngine.calculate_cagr(100, 259.37, 10)
        assert cagr == pytest.approx(10.0, 0.1)
        assert ec is None
