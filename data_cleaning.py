import pandas as pd
import os

raw_path = "data/raw"
processed_path = "data/processed"

# Make sure processed folder exists
os.makedirs(processed_path, exist_ok=True)

for file in os.listdir(raw_path):
    if file.endswith(".csv"):
        print(f"\n--- Cleaning {file} ---")
        df = pd.read_csv(os.path.join(raw_path, file))

        # Step 2: Cleaning
        # 1. Standardize column names
        df.columns = df.columns.str.lower().str.replace(" ", "_")

        # 2. Handle missing values (example: fill with empty string)
        df = df.fillna("")

        # 3. Convert date columns if any
        for col in df.columns:
            if "date" in col:
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass  # skip if not convertible

        # Save cleaned version
        cleaned_file = file.replace(".csv", "_clean.csv")
        df.to_csv(os.path.join(processed_path, cleaned_file), index=False)

        print(f"Saved cleaned file: {cleaned_file}")
