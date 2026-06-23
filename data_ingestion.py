import pandas as pd
import os

raw_path = "data/raw"

for file in os.listdir(raw_path):
    if file.endswith(".csv"):
        print(f"\n--- {file} ---")
        df = pd.read_csv(os.path.join(raw_path, file))
        print("Shape:", df.shape)
        print("Columns:\n", df.dtypes)
        print(df.head())
