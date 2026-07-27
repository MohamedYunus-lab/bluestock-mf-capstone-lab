import sqlite3
import pandas as pd

conn = sqlite3.connect('db/nifty100.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]
print("Tables:", tables)
print()

for table in tables:
    c.execute(f"SELECT COUNT(*) FROM {table}")
    count = c.fetchone()[0]
    print(f"{table}: {count} rows")

conn.close()
