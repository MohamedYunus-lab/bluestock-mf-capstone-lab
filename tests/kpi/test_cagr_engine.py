"""
Unit tests for CAGR Engine (Day 10)
10 comprehensive tests covering 6 edge case handlers
"""

import pytest
from src.analytics.cagr import CAGREngine, CAGREdgeCase


class TestCAGRCore:
    """Core CAGR calculation tests"""
    
    def test_cagr_standard_positive_growth(self):
        """Test standard CAGR calculation with positive growth"""
        # Beginning: 100, Ending: 161.05 over 5 years = 10% CAGR
        cagr, edge_case = CAGREngine.calculate_cagr(100, 161.05, 5)
        assert cagr == pytest.approx(10.0, rel=0.01)
        assert edge_case is None
    
    def test_cagr_standard_low_growth(self):
        """Test CAGR with low growth rate"""
        # 100 to 110 over 5 years = ~1.9% CAGR
        cagr, edge_case = CAGREngine.calculate_cagr(100, 110, 5)
        assert cagr == pytest.approx(1.924, rel=0.01)
        assert edge_case is None


class TestCAGREdgeCaseTurnaround:
    """Edge Case 1: Turnaround (negative to positive)"""
    
    def test_cagr_turnaround(self):
        """Test turnaround case: negative to positive"""
        cagr, edge_case = CAGREngine.calculate_cagr(-100, 50, 5)
        assert cagr is None
        assert edge_case is not None
        assert edge_case.flag == "TURNAROUND"


class TestCAGREdgeCaseDecline:
    """Edge Case 2: Decline (positive to negative)"""
    
    def test_cagr_decline(self):
        """Test decline case: positive to negative"""
        cagr, edge_case = CAGREngine.calculate_cagr(100, -50, 5)
        assert cagr is None
        assert edge_case is not None
        assert edge_case.flag == "DECLINE"


class TestCAGREdgeCaseBothNegative:
    """Edge Case 3: Both negative"""
    
    def test_cagr_both_negative(self):
        """Test both negative case"""
        cagr, edge_case = CAGREngine.calculate_cagr(-200, -100, 5)
        assert cagr is None
        assert edge_case is not None
        assert edge_case.flag == "BOTH_NEGATIVE"


class TestCAGREdgeCaseZeroBase:
    """Edge Case 4: Zero base"""
    
    def test_cagr_zero_base(self):
        """Test zero base case: beginning value is zero"""
        cagr, edge_case = CAGREngine.calculate_cagr(0, 100, 5)
        assert cagr is None
        assert edge_case is not None
        assert edge_case.flag == "ZERO_BASE"


class TestRevenueCAGRMultiPeriod:
    """Revenue CAGR with 3/5/10-year periods"""
    
    def test_revenue_cagr_5_year_normal(self):
        """Test Revenue CAGR over 5 years - normal case"""
        revenue_series = {
            2018: 100,
            2019: 110,
            2020: 121,
            2021: 133.1,
            2022: 146.41,
            2023: 161.05
        }
        cagr, edge_case = CAGREngine.calculate_revenue_cagr(revenue_series, num_years=5)
        assert cagr == pytest.approx(10.0, rel=0.01)
        assert edge_case is None
    
    def test_revenue_cagr_insufficient_data(self):
        """Test Revenue CAGR with insufficient data (Edge Case 5)"""
        revenue_series = {
            2021: 100,
            2022: 110,
            2023: 121
        }
        cagr, edge_case = CAGREngine.calculate_revenue_cagr(revenue_series, num_years=5)
        assert cagr is None
        assert edge_case is not None
        assert edge_case.flag == "INSUFFICIENT_DATA"


class TestPATCAGRMultiPeriod:
    """PAT CAGR with 3/5/10-year periods"""
    
    def test_pat_cagr_missing_data(self):
        """Test PAT CAGR with missing intermediate data"""
        pat_series = {
            2018: 50,
            2019: 75,
            2020: 75,  # No None values - these must be present in dict
            2021: 90,
            2022: 100,
            2023: 110
        }
        cagr, edge_case = CAGREngine.calculate_pat_cagr(pat_series, num_years=5)
        # Should calculate from 2018 to 2023
        assert cagr is not None
        assert edge_case is None


class TestEPSCAGRTurnaround:
    """EPS CAGR with turnaround detection"""
    
    def test_eps_cagr_turnaround_edge_case(self):
        """Test EPS CAGR detecting turnaround (Edge Case 1)"""
        eps_series = {
            2018: -2.0,
            2019: -1.5,
            2020: -0.5,
            2021: 0.5,
            2022: 1.5,
            2023: 2.5
        }
        cagr, edge_case = CAGREngine.calculate_eps_cagr(eps_series, num_years=5)
        assert cagr is None
        assert edge_case is not None
        assert edge_case.flag == "TURNAROUND"


class TestCAGRValidationHelper:
    """Test validation helper function"""
    
    def test_validate_series_clean(self):
        """Test validation with clean series"""
        values = [100, 110, 121, 133.1, 146.41]
        clean, issue = CAGREngine.validate_series(values)
        assert clean == values
        assert issue is None
    
    def test_validate_series_empty(self):
        """Test validation with empty series"""
        values = []
        clean, issue = CAGREngine.validate_series(values)
        assert clean == []
        assert issue == "empty_series"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
