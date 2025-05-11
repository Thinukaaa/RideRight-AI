import sqlite3
import pandas as pd

conn = sqlite3.connect("data/cars.db")
df = pd.read_sql_query("SELECT * FROM cars LIMIT 10", conn)
conn.close()

print(df)
