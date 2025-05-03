import sqlite3
import os

DB_PATH = os.path.join("data", "cars.db")

def connect_db():
    return sqlite3.connect(DB_PATH)

# 1. Get Cars by Budget
def get_cars_by_budget(max_price):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT brand, model, price FROM cars WHERE price <= ? ORDER BY price ASC", (max_price,))
        return cursor.fetchall()

# 2. Get Cars by Brand
def get_cars_by_brand(brand):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT model, type, price FROM cars WHERE brand LIKE ?", (f"%{brand}%",))
        return cursor.fetchall()

# 3. Get Cars by Type
def get_cars_by_type(car_type):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT brand, model, price FROM cars WHERE type LIKE ?", (f"%{car_type}%",))
        return cursor.fetchall()

# 4. Compare Cars (by model)
def compare_cars(model1, model2):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cars WHERE model IN (?, ?)", (model1, model2))
        return cursor.fetchall()

# 5. Get Trade-In Value Estimate
def get_trade_in_estimate(model, year, mileage):
    # Basic formula: (e.g., new_value - depreciation - mileage penalty)
    base_value = 20000
    age = 2025 - year
    depreciation = age * 1000
    mileage_penalty = (mileage // 10000) * 500
    estimated_value = max(2000, base_value - depreciation - mileage_penalty)
    return estimated_value

# 6. Get Dealers by Brand
def get_dealers_by_brand(brand):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, location, contact FROM dealers WHERE brand LIKE ?", (f"%{brand}%",))
        return cursor.fetchall()

# 7. Save User Preferences
def save_user_preference(user_id, brand, car_type, budget, fuel_type):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_preferences (user_id, preferred_brand, car_type, budget, fuel_type)
            VALUES (?, ?, ?, ?, ?)""", (user_id, brand, car_type, budget, fuel_type))
        conn.commit()

# 8. Get User Preferences
def get_user_preference(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT preferred_brand, car_type, budget, fuel_type FROM user_preferences WHERE user_id = ?", (user_id,))
        return cursor.fetchone()
