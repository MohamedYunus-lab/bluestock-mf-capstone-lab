"""
Data Validation Script for Power BI Dashboard
Checks if all required data files exist and contain valid data
"""

import pandas as pd
import sqlite3
import os

print("="*80)
print("POWER BI DATA VALIDATION")
print("="*80)

# Check if processed CSV files exist
csv_files = [
    "01_fund_master_clean.csv",
    "02_nav_history_clean.csv",
    "03_aum_by_fund_house_clean.csv",
    "04_monthly_sip_inflows_clean.csv",
    "05_category_inflows_clean.csv",
    "06_industry_folio_count_clean.csv",
    "07_scheme_performance_clean.csv",
    "08_investor_transactions_clean.csv",
    "09_portfolio_holdings_clean.csv",
    "10_benchmark_indices_clean.csv"
]

print("\n1. Checking CSV Files...")
all_csv_exist = True
for csv_file in csv_files:
    file_path = f"data/processed/{csv_file}"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        print(f"   ✓ {csv_file:40s} - {len(df):,} rows")
    else:
        print(f"   ✗ {csv_file:40s} - NOT FOUND")
        all_csv_exist = False

# Check SQLite database
print("\n2. Checking SQLite Database...")
if os.path.exists('bluestock_mf.db'):
    conn = sqlite3.connect('bluestock_mf.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"   ✓ Database found with {len(tables)} tables")
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        count = cursor.fetchone()[0]
        print(f"     - {table_name:40s}: {count:,} rows")
    
    conn.close()
else:
    print("   ✗ bluestock_mf.db NOT FOUND")

# Calculate key metrics
print("\n3. Calculating Key Metrics for Dashboard...")

try:
    # Total AUM
    aum_df = pd.read_csv("data/processed/03_aum_by_fund_house_clean.csv")
    total_aum = aum_df['aum_crore'].sum() / 100000  # Convert to Lakh Crore
    print(f"   Total AUM: ₹{total_aum:,.2f} Lakh Cr")
    
    # SIP Inflows
    sip_df = pd.read_csv("data/processed/04_monthly_sip_inflows_clean.csv")
    max_sip = sip_df['sip_inflow_crore'].max()
    print(f"   Peak SIP Inflow: ₹{max_sip:,.2f} Cr")
    
    # Folios
    folio_df = pd.read_csv("data/processed/06_industry_folio_count_clean.csv")
    max_folios = folio_df['total_folios_crore'].max()
    print(f"   Total Folios: {max_folios:.2f} Cr")
    
    # Schemes
    fund_df = pd.read_csv("data/processed/01_fund_master_clean.csv")
    total_schemes = len(fund_df)
    print(f"   Total Schemes: {total_schemes:,}")
    
    print("\n4. Data Quality Checks...")
    
    # Check for missing amfi_code
    if fund_df['amfi_code'].isna().sum() > 0:
        print(f"   ⚠ Warning: {fund_df['amfi_code'].isna().sum()} missing AMFI codes in fund_master")
    else:
        print(f"   ✓ No missing AMFI codes in fund_master")
    
    # Check date formats
    nav_df = pd.read_csv("data/processed/02_nav_history_clean.csv")
    nav_df['date'] = pd.to_datetime(nav_df['date'], errors='coerce')
    if nav_df['date'].isna().sum() > 0:
        print(f"   ⚠ Warning: {nav_df['date'].isna().sum()} invalid dates in nav_history")
    else:
        print(f"   ✓ All dates valid in nav_history")
    
    print("\n" + "="*80)
    print("DATA VALIDATION COMPLETE")
    print("="*80)
    print("\nYou can now proceed with Power BI dashboard creation.")
    print("Follow the instructions in POWER_BI_GUIDE.txt")
    
except Exception as e:
    print(f"\n   ✗ Error during validation: {str(e)}")

print("\n")
