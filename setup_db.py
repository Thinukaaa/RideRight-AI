import sqlite3
import os

DB_PATH = os.path.join("data", "cars.db")

def create_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Cars table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT,
            model TEXT,
            type TEXT,
            price INTEGER,
            fuel_type TEXT,
            mileage INTEGER,
            year INTEGER,
            transmission TEXT,
            seats INTEGER
        )
    ''')

    # Trade-in table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_in (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            brand TEXT,
            model TEXT,
            year INTEGER,
            mileage INTEGER,
            estimated_value INTEGER
        )
    ''')

    # User preferences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            preferred_brand TEXT,
            car_type TEXT,
            budget INTEGER,
            fuel_type TEXT
        )
    ''')

    # Dealers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dealers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            brand TEXT,
            location TEXT,
            contact TEXT
        )
    ''')

    # ✅ Sample Trade-in entries
    trade_ins = [
        ("Alice", "Toyota", "Yaris", 2015, 85000, 6500),
        ("Bob", "Ford", "Focus", 2016, 92000, 5800),
        ("Charlie", "Hyundai", "i20", 2017, 70000, 7200)
    ]
    cursor.executemany('''
        INSERT INTO trade_in (user_name, brand, model, year, mileage, estimated_value)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', trade_ins)

    # ✅ Sample user preferences
    prefs = [
        ("user_1", "Honda", "SUV", 30000, "Hybrid"),
        ("user_2", "Tesla", "Sedan", 50000, "EV"),
        ("user_3", "Toyota", "Hatchback", 25000, "Petrol")
    ]
    cursor.executemany('''
        INSERT INTO user_preferences (user_id, preferred_brand, car_type, budget, fuel_type)
        VALUES (?, ?, ?, ?, ?)
    ''', prefs)

    # ✅ Sample dealers
    dealers = [
        ("City AutoMart", "Toyota", "New York", "ny-toyota@dealers.com"),
        ("DriveHub Motors", "Ford", "Los Angeles", "la-ford@dealers.com"),
        ("Premier Auto", "BMW", "Chicago", "chicago-bmw@dealers.com"),
        ("EV Central", "Tesla", "San Francisco", "sf-tesla@dealers.com")
    ]
    cursor.executemany('''
        INSERT INTO dealers (name, brand, location, contact)
        VALUES (?, ?, ?, ?)
    ''', dealers)

    conn.commit()
    conn.close()
    print("✅ Database schema created and sample data inserted.")

# 🔧 RUN
if __name__ == "__main__":
    create_db()
