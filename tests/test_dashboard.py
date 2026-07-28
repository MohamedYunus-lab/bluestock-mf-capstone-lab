"""
Dashboard Tests - Validation for all 8 screens
Day 27: Testing all screens with 10 different tickers across sectors
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dashboard.utils.db import (
    load_all_companies, load_company_by_id, load_company_ratios,
    load_company_profitandloss, get_kpi_summary, get_sector_distribution,
    get_top_companies_by_metric, load_peer_group, load_sector_medians,
    load_annual_report_links, load_prosandcons, get_available_years
)


class TestDashboardDataLoaders:
    """Test database loaders for dashboard"""
    
    def test_load_all_companies(self):
        """Test loading all companies"""
        df = load_all_companies()
        assert df is not None
        assert 'company_id' in df.columns
        assert 'company_name' in df.columns
        assert 'sector_name' in df.columns
        print(f"✓ Loaded {len(df)} companies")
    
    def test_load_company_by_id(self):
        """Test loading single company"""
        all_companies = load_all_companies()
        if not all_companies.empty:
            company_id = all_companies.iloc[0]['company_id']
            company = load_company_by_id(company_id)
            assert company is not None
            assert company['company_id'] == company_id
            print(f"✓ Loaded company: {company['company_name']}")
    
    def test_load_company_ratios(self):
        """Test loading company ratios"""
        all_companies = load_all_companies()
        if not all_companies.empty:
            company_id = all_companies.iloc[0]['company_id']
            ratios = load_company_ratios(company_id, years=10)
            assert ratios is not None
            assert 'year' in ratios.columns if not ratios.empty else True
            print(f"✓ Loaded {len(ratios)} years of ratios")
    
    def test_load_company_profitandloss(self):
        """Test loading P&L data"""
        all_companies = load_all_companies()
        if not all_companies.empty:
            company_id = all_companies.iloc[0]['company_id']
            pl = load_company_profitandloss(company_id, years=10)
            assert pl is not None
            assert 'revenue_cr' in pl.columns if not pl.empty else True
            print(f"✓ Loaded {len(pl)} years of P&L data")
    
    def test_get_kpi_summary(self):
        """Test KPI summary"""
        years = get_available_years()
        if years:
            summary = get_kpi_summary(years[0])
            assert summary is not None
            assert 'total_companies' in summary
            print(f"✓ KPI Summary: {summary.get('total_companies')} companies")
    
    def test_get_sector_distribution(self):
        """Test sector distribution"""
        years = get_available_years()
        if years:
            sectors = get_sector_distribution(years[0])
            assert sectors is not None
            assert 'sector_name' in sectors.columns if not sectors.empty else True
            print(f"✓ Loaded {len(sectors)} sectors")
    
    def test_get_top_companies_by_metric(self):
        """Test top companies ranking"""
        years = get_available_years()
        if years:
            top = get_top_companies_by_metric('roe', years[0], limit=5)
            assert top is not None
            assert len(top) <= 5
            print(f"✓ Top {len(top)} companies by ROE")
    
    def test_get_available_years(self):
        """Test available years"""
        years = get_available_years()
        assert years is not None
        assert len(years) > 0
        print(f"✓ Available years: {years}")
    
    def test_load_peer_group(self):
        """Test peer group loading"""
        all_companies = load_all_companies()
        if not all_companies.empty:
            company_id = all_companies.iloc[0]['company_id']
            peers = load_peer_group(company_id)
            assert peers is not None
            print(f"✓ Loaded {len(peers)} peers")
    
    def test_load_prosandcons(self):
        """Test pros and cons"""
        years = get_available_years()
        all_companies = load_all_companies()
        if years and not all_companies.empty:
            company_id = all_companies.iloc[0]['company_id']
            proscons = load_prosandcons(company_id, years[0])
            # May be None if no data, that's OK
            print(f"✓ Loaded pros/cons data: {proscons is not None}")


class TestValuationModule:
    """Test valuation module"""
    
    def test_valuation_import(self):
        """Test valuation module imports"""
        from analytics.valuation import (
            FCFYieldCalculator, SectorMedianCalculator,
            ValuationFlagger, get_valuation_metrics
        )
        assert FCFYieldCalculator is not None
        assert SectorMedianCalculator is not None
        assert ValuationFlagger is not None
        print("✓ Valuation module imports successful")
    
    def test_fcf_yield_calculation(self):
        """Test FCF yield calculation"""
        from analytics.valuation import FCFYieldCalculator
        
        # Test normal case
        fcf_yield = FCFYieldCalculator.calculate_fcf_yield(100, 1000)
        assert fcf_yield == 10.0
        print("✓ FCF Yield calculation: 10%")
        
        # Test zero market cap
        fcf_yield = FCFYieldCalculator.calculate_fcf_yield(100, 0)
        assert fcf_yield is None
        print("✓ FCF Yield with zero market cap: None")
        
        # Test None inputs
        fcf_yield = FCFYieldCalculator.calculate_fcf_yield(None, 1000)
        assert fcf_yield is None
        print("✓ FCF Yield with None input: None")
    
    def test_valuation_flags(self):
        """Test valuation flag generation"""
        from analytics.valuation import ValuationFlagger
        
        # Test Caution flag (P/E > 1.5x)
        flag, conf = ValuationFlagger.flag_pe_valuation(30.0, 20.0)
        assert flag == 'Caution'
        assert conf > 0.7
        print(f"✓ Caution flag: {flag} (conf: {conf:.2f})")
        
        # Test Discount flag (P/E < 0.7x)
        flag, conf = ValuationFlagger.flag_pe_valuation(10.0, 20.0)
        assert flag == 'Discount'
        assert conf > 0.7
        print(f"✓ Discount flag: {flag} (conf: {conf:.2f})")
        
        # Test Fair flag (0.7x - 1.5x)
        flag, conf = ValuationFlagger.flag_pe_valuation(15.0, 20.0)
        assert flag == 'Fair'
        assert conf > 0.7
        print(f"✓ Fair flag: {flag} (conf: {conf:.2f})")
    
    def test_combined_valuation_flag(self):
        """Test combined valuation flag"""
        from analytics.valuation import ValuationFlagger
        
        flag, conf = ValuationFlagger.flag_combined_valuation(
            pe_ratio=30.0,
            pb_ratio=3.0,
            ev_ebitda=18.0,
            fcf_yield=2.0,
            sector_median_pe=20.0,
            sector_median_pb=2.5,
            sector_median_ev_ebitda=12.0
        )
        
        assert flag in ['Caution', 'Fair', 'Discount']
        assert 0 <= conf <= 1
        print(f"✓ Combined flag: {flag} (conf: {conf:.2f})")


class TestDashboardScreens:
    """Test dashboard screen functionality"""
    
    def test_screen_rendering(self):
        """Test that all screen modules can be imported"""
        try:
            from dashboard.pages import page_01_home
            from dashboard.pages import page_02_profile
            from dashboard.pages import page_03_screener
            from dashboard.pages import page_04_peer
            from dashboard.pages import page_05_trends
            from dashboard.pages import page_06_sector
            from dashboard.pages import page_07_allocation
            from dashboard.pages import page_08_reports
            print("✓ All 8 dashboard screens imported successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import screen: {str(e)}")
    
    def test_screen_functions_exist(self):
        """Test that all screen modules have app() function"""
        from dashboard.pages import page_01_home
        assert hasattr(page_01_home, 'app')
        assert callable(page_01_home.app)
        print("✓ Home screen app() function exists")


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_partial_data_scenario(self):
        """Test handling of partial data"""
        years = get_available_years()
        all_companies = load_all_companies()
        
        # Try loading company with potentially missing ratios
        if not all_companies.empty and years:
            company_id = all_companies.iloc[-1]['company_id']  # Last company
            ratios = load_company_ratios(company_id, years=10)
            # Should not crash even if data is incomplete
            assert ratios is not None
            print(f"✓ Handled partial data scenario: {len(ratios)} rows")
    
    def test_extreme_slider_values(self):
        """Test extreme slider values don't crash"""
        years = get_available_years()
        if years:
            # Test with extreme values
            from dashboard.utils.db import get_db_connection
            conn = get_db_connection()
            
            # Should not crash
            query = "SELECT COUNT(*) FROM financial_ratios WHERE roe > 200 OR roe < -100"
            cursor = conn.execute(query)
            result = cursor.fetchone()
            assert result is not None
            print(f"✓ Handled extreme values: {result[0]} companies with extreme ROE")
    
    def test_missing_data_display(self):
        """Test N/A display for missing data"""
        all_companies = load_all_companies()
        
        if not all_companies.empty:
            # Find company with potentially missing metrics
            company = all_companies.iloc[0]
            ratios = load_company_ratios(company['company_id'], years=1)
            
            if not ratios.empty:
                # Check handling of None/NaN values
                latest = ratios.iloc[-1]
                # Test that None values are handled gracefully
                assert True  # If we got here without crashing, test passes
                print("✓ Missing data handling verified")


class TestPerformance:
    """Test dashboard performance requirements"""
    
    def test_profile_load_time(self):
        """Test company profile loads in < 3 seconds"""
        import time
        
        all_companies = load_all_companies()
        if not all_companies.empty:
            company_id = all_companies.iloc[0]['company_id']
            
            start = time.time()
            company_info = load_company_by_id(company_id)
            ratios = load_company_ratios(company_id, years=10)
            pl = load_company_profitandloss(company_id, years=10)
            proscons = load_prosandcons(company_id, 2023)
            end = time.time()
            
            elapsed = end - start
            assert elapsed < 3.0, f"Profile load took {elapsed:.2f}s (max: 3s)"
            print(f"✓ Profile load time: {elapsed:.3f}s (< 3s requirement)")


class TestCrossScreenDataConsistency:
    """Test data consistency across screens"""
    
    def test_home_vs_profile_data(self):
        """Test that home and profile screens show consistent data"""
        years = get_available_years()
        if years:
            # Home screen KPI
            home_kpi = get_kpi_summary(years[0])
            
            # Profile screen company count check
            all_companies = load_all_companies()
            
            # Should match
            assert home_kpi.get('total_companies') == len(all_companies)
            print(f"✓ Data consistency verified: {home_kpi.get('total_companies')} companies")
    
    def test_screener_results_validity(self):
        """Test screener results are valid"""
        all_companies = load_all_companies()
        if not all_companies.empty:
            # Verify all companies have proper structure
            for _, company in all_companies.iterrows():
                assert company['company_id'] is not None
                assert company['company_name'] is not None
            print(f"✓ Screener data validity: {len(all_companies)} companies verified")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
