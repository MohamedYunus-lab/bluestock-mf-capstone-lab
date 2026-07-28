"""
Data Cleaning Script
Cleans and standardizes all raw datasets
Author: Mohamed Yunus
Date: June 2026
"""

import pandas as pd
import os

raw_path = "data/raw"
processed_path = "data/processed"

os.makedirs(processed_path, exist_ok=True)

print("=" * 80)
print("DATA CLEANING PROCESS")
print("=" * 80)

for file in os.listdir(raw_path):
    if file.endswith(".csv") and not file.startswith("live_nav"):
        print(f"\nCleaning {file}")
        df = pd.read_csv(os.path.join(raw_path, file))

        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(" ", "_")

        # Handle missing values
        df = df.fillna("")

        # Convert date columns
        for col in df.columns:
            if "date" in col:
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

        # Save cleaned version
        cleaned_file = file.replace(".csv", "_clean.csv")
        df.to_csv(os.path.join(processed_path, cleaned_file), index=False)

        print(f"  Saved: {cleaned_file}")
        print(f"  Rows: {len(df)}, Columns: {len(df.columns)}")

print("\n" + "=" * 80)
print("DATA CLEANING COMPLETE")
print("=" * 80)
print(f"\nCleaned files saved in: {processed_path}")
