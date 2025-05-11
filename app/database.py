import sqlite3
import os

DB_PATH = os.path.join("data", "cars.db")

def create_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        type TEXT NOT NULL,
        price INTEGER NOT NULL,
        fuel_type TEXT,
        mileage INTEGER,
        year INTEGER,
        transmission TEXT,
        seats INTEGER,
        image TEXT
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database created successfully.")

def insert_sample_data():
    sample_data = [
        ("Toyota", "Corolla", "Sedan", 23000, "Petrol", 30, 2022, "Automatic", 5, ""),
        ("Honda", "Civic", "Sedan", 25000, "Petrol", 32, 2022, "Manual", 5, ""),
        ("Ford", "Escape", "SUV", 29000, "Hybrid", 28, 2023, "Automatic", 5, ""),
        ("Nissan", "Leaf", "Hatchback", 27000, "EV", 110, 2023, "Automatic", 5, ""),
        ("BMW", "X3", "SUV", 45000, "Diesel", 25, 2022, "Automatic", 5, "")
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executemany('''
    INSERT INTO cars (brand, model, type, price, fuel_type, mileage, year, transmission, seats, image)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_data)

    conn.commit()
    conn.close()
    print("🚗 Sample data inserted successfully.")
