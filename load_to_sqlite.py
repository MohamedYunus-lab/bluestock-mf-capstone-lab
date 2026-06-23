import pandas as pd
import sqlite3
import os

processed_path = "data/processed"
db_path = "bluestock_mf.db"
conn = sqlite3.connect(db_path)

for file in os.listdir(processed_path):
    if file.endswith("_clean.csv"):
        table_name = file.replace("_clean.csv", "")
        print(f"Loading {file} into table {table_name}...")

        df = pd.read_csv(os.path.join(processed_path, file))
        df.to_sql(table_name, conn, if_exists="replace", index=False)

conn.close()
print("All tables loaded into bluestock_mf.db")
