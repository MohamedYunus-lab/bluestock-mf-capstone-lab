"""
Unit Tests for Data Normaliser
Test normalize_year, normalize_ticker, and other normalization functions
"""

import pytest
from src.etl.normaliser import normalize_year, normalize_ticker, normalize_numeric, normalize_string


class TestNormalizeYear:
    """Test normalize_year function"""
    
    def test_normalize_year_valid_integer(self):
        assert normalize_year(2023) == 2023
        assert normalize_year(2024) == 2024
        assert normalize_year(2000) == 2000
    
    def test_normalize_year_string_integer(self):
        assert normalize_year("2023") == 2023
        assert normalize_year("2024") == 2024
        assert normalize_year("2000") == 2000
    
    def test_normalize_year_with_commas(self):
        assert normalize_year("2,023") == 2023
        assert normalize_year("2,024") == 2024
    
    def test_normalize_year_fy_format(self):
        assert normalize_year("FY2023") == 2023
        assert normalize_year("FY 2024") == 2024
        assert normalize_year("fy2023") == 2023
    
    def test_normalize_year_range_format(self):
        assert normalize_year("2023-2024") == 2023
        assert normalize_year("2023/2024") == 2023
        assert normalize_year("2023-24") == 2023
    
    def test_normalize_year_two_digit(self):
        assert normalize_year("23") == 2023
        assert normalize_year("24") == 2024
        assert normalize_year("99") == 1999
        assert normalize_year("00") == 2000
    
    def test_normalize_year_float(self):
        assert normalize_year(2023.5) == 2023
        assert normalize_year(2024.9) == 2024
    
    def test_normalize_year_invalid(self):
        assert normalize_year(None) is None
        assert normalize_year("") is None
        assert normalize_year("abc") is None
        assert normalize_year(1800) is None
        assert normalize_year(2200) is None
    
    def test_normalize_year_with_y_prefix(self):
        assert normalize_year("Y2023") == 2023
        assert normalize_year("y2024") == 2024


class TestNormalizeTicker:
    """Test normalize_ticker function"""
    
    def test_normalize_ticker_valid(self):
        assert normalize_ticker("INFY") == "INFY"
        assert normalize_ticker("TCS") == "TCS"
        assert normalize_ticker("RELIANCE") == "RELIANCE"
    
    def test_normalize_ticker_lowercase(self):
        assert normalize_ticker("infy") == "INFY"
        assert normalize_ticker("tcs") == "TCS"
        assert normalize_ticker("InFy") == "INFY"
    
    def test_normalize_ticker_with_whitespace(self):
        assert normalize_ticker("  INFY  ") == "INFY"
        assert normalize_ticker(" TCS ") == "TCS"
    
    def test_normalize_ticker_with_ampersand(self):
        assert normalize_ticker("M&M") == "M&M"
        assert normalize_ticker("L&T") == "L&T"
    
    def test_normalize_ticker_with_hyphen(self):
        assert normalize_ticker("HDFC-Bank") == "HDFCBANK"
        assert normalize_ticker("STATE-BANK") == "STATEBANK"
    
    def test_normalize_ticker_with_numbers(self):
        assert normalize_ticker("HDFC10") == "HDFC10"
        assert normalize_ticker("INFY50") == "INFY50"
    
    def test_normalize_ticker_invalid(self):
        assert normalize_ticker(None) is None
        assert normalize_ticker("") is None
        assert normalize_ticker("   ") is None
        assert normalize_ticker("123ABC") is None
        assert normalize_ticker("1234") is None
    
    def test_normalize_ticker_special_characters(self):
        assert normalize_ticker("INFY@#") == "INFY"
        assert normalize_ticker("TCS!@#") == "TCS"
    
    def test_normalize_ticker_too_long(self):
        assert normalize_ticker("VERYLONGTICKERSYMBOL") is None
    
    def test_normalize_ticker_too_short(self):
        assert normalize_ticker("") is None


class TestNormalizeNumeric:
    """Test normalize_numeric function"""
    
    def test_normalize_numeric_valid(self):
        assert normalize_numeric("100.5") == 100.5
        assert normalize_numeric("1000") == 1000.0
        assert normalize_numeric("0.05") == 0.05
    
    def test_normalize_numeric_with_commas(self):
        assert normalize_numeric("1,000.5") == 1000.5
        assert normalize_numeric("1,000,000") == 1000000.0
    
    def test_normalize_numeric_negative(self):
        assert normalize_numeric("-100.5", allow_negative=True) == -100.5
        assert normalize_numeric("-100.5", allow_negative=False) is None
    
    def test_normalize_numeric_invalid(self):
        assert normalize_numeric(None) is None
        assert normalize_numeric("") is None
        assert normalize_numeric("abc") is None
        assert normalize_numeric("NA") is None
        assert normalize_numeric("N/A") is None
    
    def test_normalize_numeric_float_input(self):
        assert normalize_numeric(100.5) == 100.5
        assert normalize_numeric(1000) == 1000.0


class TestNormalizeString:
    """Test normalize_string function"""
    
    def test_normalize_string_valid(self):
        assert normalize_string("Hello World") == "Hello World"
        assert normalize_string("Test String") == "Test String"
    
    def test_normalize_string_whitespace(self):
        assert normalize_string("  Hello  World  ") == "Hello World"
        assert normalize_string("\n\tTest\t\n") == "Test"
    
    def test_normalize_string_max_length(self):
        long_string = "a" * 300
        result = normalize_string(long_string, max_length=255)
        assert len(result) == 255
    
    def test_normalize_string_invalid(self):
        assert normalize_string(None) is None
        assert normalize_string("") is None
        assert normalize_string("   ") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
