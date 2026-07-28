"""
Database Load Script
Loads cleaned data into SQLite database using star schema
Author: Mohamed Yunus
Date: June 2026
"""

import pandas as pd
import sqlite3
import os

processed_path = "data/processed"
db_path = "bluestock_mf.db"
schema_path = "sql/schema.sql"

print("=" * 80)
print("LOADING DATA INTO SQLITE DATABASE")
print("=" * 80)

# Create database and execute schema
print("\nCreating database schema from sql/schema.sql")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

if os.path.exists(schema_path):
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        for statement in schema_sql.split(';'):
            if statement.strip():
                try:
                    cursor.execute(statement)
                except Exception as e:
                    print(f"  Note: {str(e)[:60]}")
    conn.commit()
    print("  Schema created successfully")
else:
    print("  Warning: schema.sql not found")

# Map CSV files to database tables
table_mapping = {
    "01_fund_master_clean.csv": "dim_fund",
    "02_nav_history_clean.csv": "fact_nav",
    "03_aum_by_fund_house_clean.csv": "fact_aum",
    "04_monthly_sip_inflows_clean.csv": "fact_sip_industry",
    "05_category_inflows_clean.csv": "fact_category_inflows",
    "06_industry_folio_count_clean.csv": "fact_folio_count",
    "07_scheme_performance_clean.csv": "fact_performance",
    "08_investor_transactions_clean.csv": "fact_transactions",
    "09_portfolio_holdings_clean.csv": "fact_portfolio",
    "10_benchmark_indices_clean.csv": "fact_benchmark"
}

print("\nLoading cleaned datasets into database")
print("-" * 80)

for file, table_name in table_mapping.items():
    file_path = os.path.join(processed_path, file)
    
    if os.path.exists(file_path):
        print(f"\n  Loading {file} -> {table_name}")
        try:
            df = pd.read_csv(file_path)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            
            cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
            count = cursor.fetchone()[0]
            print(f"  Loaded {count} rows")
            
        except Exception as e:
            print(f"  Error: {str(e)}")
    else:
        print(f"  Warning: {file} not found")

# Verify database
print("\n" + "=" * 80)
print("DATABASE VERIFICATION")
print("=" * 80)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"\nTotal tables created: {len(tables)}")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM '{table[0]}'")
    count = cursor.fetchone()[0]
    print(f"  {table[0]}: {count:,} records")

conn.close()

print("\n" + "=" * 80)
print("DATABASE SETUP COMPLETE")
print("=" * 80)
print(f"\nDatabase: {db_path}")
print(f"Size: {os.path.getsize(db_path) / (1024*1024):.2f} MB")
print("\nNext Steps:")
print("  1. Run queries from sql/queries.sql")
print("  2. Begin exploratory data analysis")
print("  3. Start Day 3 tasks")
