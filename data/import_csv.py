import sqlite3
import pandas as pd

CSV_PATH = "data/car_inventory_clean.csv"
DB_PATH = "data/cars.db"

def import_data():
    df = pd.read_csv(CSV_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO cars (brand, model, type, price, fuel_type, mileage, year, transmission, seats)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['brand'], row['model'], row['type'],
            int(row['price']), row['fuel_type'], int(row['mileage']),
            int(row['year']), row['transmission'], int(row['seats'])
        ))

    conn.commit()
    conn.close()
    print("✅ Data imported from 'car_inventory_clean.csv' into 'cars.db'")

if __name__ == "__main__":
    import_data()
