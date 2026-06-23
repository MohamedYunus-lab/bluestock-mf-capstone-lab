"""
Live NAV Data Fetch Script
Fetches historical NAV data from mfapi.in for selected mutual fund schemes
Author: Mohamed Yunus
Date: June 2026
"""

import requests
import pandas as pd
import os

# Ensure raw data directory exists
os.makedirs("data/raw", exist_ok=True)

# Scheme codes as per project requirements
schemes = {
    "125497": "HDFC_Top_100_Direct",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip", 
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip"
}

print("Starting NAV data fetch from mfapi.in")
print("-" * 60)

for scheme_code, scheme_name in schemes.items():
    try:
        print(f"\nFetching data for {scheme_name} (Code: {scheme_code})")
        
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            fund_name = data.get('meta', {}).get('scheme_name', 'Unknown')
            fund_house = data.get('meta', {}).get('fund_house', 'Unknown')
            
            print(f"  Fund Name: {fund_name}")
            print(f"  AMC: {fund_house}")
            
            nav_data = data.get('data', [])
            
            if nav_data:
                df = pd.DataFrame(nav_data)
                df['scheme_code'] = scheme_code
                df['scheme_name'] = scheme_name
                
                filename = f"data/raw/live_nav_{scheme_code}_{scheme_name}.csv"
                df.to_csv(filename, index=False)
                
                print(f"  Records saved: {len(df)}")
                print(f"  Latest NAV: Rs.{df.iloc[0]['nav']} (Date: {df.iloc[0]['date']})")
            else:
                print(f"  Warning: No NAV data available")
                
        else:
            print(f"  Error: API returned status {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"  Error: Request timeout")
    except requests.exceptions.RequestException as e:
        print(f"  Error: {str(e)}")
    except Exception as e:
        print(f"  Unexpected error: {str(e)}")

print("\n" + "-" * 60)
print("NAV data fetch completed")
print("Files saved in data/raw/ directory")
