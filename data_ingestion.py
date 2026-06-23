"""
Data Ingestion Script
Loads and validates all raw CSV datasets
Author: Mohamed Yunus
Date: June 2026
"""

import pandas as pd
import os

raw_path = "data/raw"

print("=" * 80)
print("DATA INGESTION AND EXPLORATION")
print("=" * 80)

# Load all datasets
print("\nLoading datasets from data/raw/")
print("-" * 80)

datasets = {}

for file in os.listdir(raw_path):
    if file.endswith(".csv") and not file.startswith("live_nav"):
        print(f"\n{file}")
        df = pd.read_csv(os.path.join(raw_path, file))
        print(f"  Shape: {df.shape[0]} rows x {df.shape[1]} columns")
        print(f"  Columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
        print(f"  Data types: {df.dtypes.value_counts().to_dict()}")
        print(f"  Sample data:")
        print(df.head(2).to_string(index=False))
        
        datasets[file.replace('.csv', '')] = df

# Fund Master Exploration
print("\n" + "=" * 80)
print("FUND MASTER EXPLORATION")
print("=" * 80)

fund_master_file = "01_fund_master.csv"
if fund_master_file in [f for f in os.listdir(raw_path) if f.endswith('.csv')]:
    fund_master = pd.read_csv(os.path.join(raw_path, fund_master_file))
    
    print(f"\nUnique Fund Houses ({fund_master['fund_house'].nunique()}):")
    print("  " + ", ".join(fund_master['fund_house'].unique()[:10]))
    if fund_master['fund_house'].nunique() > 10:
        print(f"  ... and {fund_master['fund_house'].nunique() - 10} more")
    
    print(f"\nUnique Categories ({fund_master['category'].nunique()}):")
    print("  " + ", ".join(fund_master['category'].unique()))
    
    if 'sub_category' in fund_master.columns:
        print(f"\nUnique Sub-Categories ({fund_master['sub_category'].nunique()}):")
        for cat in fund_master['sub_category'].unique()[:15]:
            print(f"  - {cat}")
        if fund_master['sub_category'].nunique() > 15:
            print(f"  ... and {fund_master['sub_category'].nunique() - 15} more")
    
    if 'risk_category' in fund_master.columns:
        print(f"\nRisk Grades Distribution:")
        risk_counts = fund_master['risk_category'].value_counts()
        for risk, count in risk_counts.items():
            print(f"  - {risk}: {count} schemes")
    
    print(f"\nAMFI Code Structure:")
    print(f"  Total schemes: {len(fund_master)}")
    print(f"  Sample codes: {fund_master['amfi_code'].head(5).tolist()}")
    
    datasets['fund_master'] = fund_master

# AMFI Code Validation
print("\n" + "=" * 80)
print("AMFI CODE VALIDATION")
print("=" * 80)

nav_history_file = "02_nav_history.csv"
if nav_history_file in [f for f in os.listdir(raw_path) if f.endswith('.csv')]:
    nav_history = pd.read_csv(os.path.join(raw_path, nav_history_file))
    
    if 'fund_master' in datasets:
        fund_master_codes = set(datasets['fund_master']['amfi_code'].unique())
        nav_history_codes = set(nav_history['amfi_code'].unique())
        
        print(f"\nData Quality Summary:")
        print(f"  Fund Master schemes: {len(fund_master_codes)}")
        print(f"  NAV History schemes: {len(nav_history_codes)}")
        
        missing_in_nav = fund_master_codes - nav_history_codes
        extra_in_nav = nav_history_codes - fund_master_codes
        
        if len(missing_in_nav) == 0:
            print(f"  All {len(fund_master_codes)} fund master codes have NAV data")
        else:
            print(f"  Warning: {len(missing_in_nav)} fund master codes missing NAV data:")
            for code in list(missing_in_nav)[:5]:
                print(f"    - {code}")
        
        if len(extra_in_nav) == 0:
            print(f"  No orphan NAV records found")
        else:
            print(f"  Note: {len(extra_in_nav)} NAV codes not in fund master")
        
        if 'date' in nav_history.columns:
            nav_history['date'] = pd.to_datetime(nav_history['date'], errors='coerce')
            print(f"\nNAV History Date Range:")
            print(f"  From: {nav_history['date'].min()}")
            print(f"  To: {nav_history['date'].max()}")
            print(f"  Total trading days: {nav_history['date'].nunique()}")
        
        validation_status = 'PASSED' if len(missing_in_nav) == 0 else 'NEEDS ATTENTION'
        print(f"\nValidation Status: {validation_status}")

print("\n" + "=" * 80)
print("DATA INGESTION COMPLETE")
print("=" * 80)
print("\nNext Steps:")
print("  1. Run data_cleaning.py to clean all datasets")
print("  2. Run load_to_sqlite.py to create database")
print("  3. Review data_dictionary.md documentation")
