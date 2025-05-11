import sqlite3

conn = sqlite3.connect("data/cars.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM cars")
count = cursor.fetchone()[0]

print(f"Total cars in database: {count}")
conn.close()
