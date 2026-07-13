"""
Data Normaliser Module
Handles normalization of year and ticker data
"""

import re
from typing import Union, Optional


def normalize_year(year: Union[str, int, float]) -> Optional[int]:
    """
    Normalize year values to integer format
    Handles: strings, integers, floats, FY formats
    Returns: integer year or None if invalid
    """
    if year is None or (isinstance(year, float) and year != year):
        return None
    
    year_str = str(year).strip()
    
    if not year_str or year_str.lower() == 'nan':
        return None
    
    year_str = year_str.replace(',', '').strip()
    
    if year_str.upper().startswith('FY'):
        year_str = year_str[2:].strip()
    
    if year_str.upper().startswith('Y'):
        year_str = year_str[1:].strip()
    
    if '-' in year_str:
        year_str = year_str.split('-')[0].strip()
    
    if '/' in year_str:
        year_str = year_str.split('/')[0].strip()
    
    try:
        year_int = int(year_str)
        
        if 1900 <= year_int <= 2100:
            return year_int
        
        if 0 <= year_int <= 99:
            if year_int < 30:
                return 2000 + year_int
            else:
                return 1900 + year_int
        
        return None
    except (ValueError, TypeError):
        return None


def normalize_ticker(ticker: str) -> Optional[str]:
    """
    Normalize stock ticker symbols
    Handles: whitespace, case, invalid characters
    Returns: normalized ticker or None if invalid
    """
    if ticker is None or (isinstance(ticker, float) and ticker != ticker):
        return None
    
    ticker_str = str(ticker).strip()
    
    if not ticker_str or ticker_str.upper() == 'NAN':
        return None
    
    ticker_str = ticker_str.upper().strip()
    
    ticker_str = re.sub(r'[^A-Z0-9&\-]', '', ticker_str)
    
    if not ticker_str or len(ticker_str) < 1 or len(ticker_str) > 10:
        return None
    
    if ticker_str[0].isdigit():
        return None
    
    return ticker_str


def normalize_numeric(value: Union[str, int, float], allow_negative: bool = True) -> Optional[float]:
    """
    Normalize numeric values
    Handles: strings, commas, special characters
    Returns: float or None if invalid
    """
    if value is None or (isinstance(value, float) and value != value):
        return None
    
    value_str = str(value).strip()
    
    if not value_str or value_str.upper() == 'NAN':
        return None
    
    value_str = value_str.replace(',', '').replace(' ', '')
    
    if value_str.upper() in ['NA', 'N/A', '-', 'NULL']:
        return None
    
    try:
        num = float(value_str)
        
        if not allow_negative and num < 0:
            return None
        
        return num
    except (ValueError, TypeError):
        return None


def normalize_string(text: str, max_length: int = 255) -> Optional[str]:
    """
    Normalize string values
    Handles: whitespace, length, special characters
    Returns: normalized string or None if invalid
    """
    if text is None:
        return None
    
    text_str = str(text).strip()
    
    if not text_str:
        return None
    
    text_str = ' '.join(text_str.split())
    
    if len(text_str) > max_length:
        text_str = text_str[:max_length]
    
    return text_str
