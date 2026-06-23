import pandas as pd
import os

raw_path = "data/raw"
processed_path = "data/processed"

os.makedirs(processed_path, exist_ok=True)

for file in os.listdir(raw_path):
    if file.endswith(".csv"):
        print(f"\n--- Cleaning {file} ---")
        df = pd.read_csv(os.path.join(raw_path, file))

        # Cleaning
        df.columns = df.columns.str.lower().str.replace(" ", "_")

        df = df.fillna("")

        for col in df.columns:
            if "date" in col:
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass  

        cleaned_file = file.replace(".csv", "_clean.csv")
        df.to_csv(os.path.join(processed_path, cleaned_file), index=False)

        print(f"Saved cleaned file: {cleaned_file}")
