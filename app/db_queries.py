import sqlite3

DB_PATH = "data/cars.db"

def get_filtered_cars(brand=None, car_type=None, fuel_type=None, transmission=None, seats=None, budget=None, min_budget=None, max_budget=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT brand, model, type, price, fuel_type, transmission, seats FROM cars WHERE 1=1"
    params = []

    if brand:
        query += " AND brand = ?"
        params.append(brand)
    if car_type:
        query += " AND type = ?"
        params.append(car_type)
    if fuel_type:
        query += " AND fuel_type = ?"
        params.append(fuel_type)
    if transmission:
        query += " AND transmission = ?"
        params.append(transmission)
    if seats:
        query += " AND seats = ?"
        params.append(seats)
    if budget:
        query += " AND price <= ?"
        params.append(budget)
    if min_budget:
        query += " AND price >= ?"
        params.append(min_budget)
    if max_budget:
        query += " AND price <= ?"
        params.append(max_budget)

    query += " ORDER BY price ASC LIMIT 10"
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

def get_cars_by_brand(brand):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT brand, model, type, price, fuel_type, transmission, seats
        FROM cars
        WHERE brand = ?
        ORDER BY price ASC LIMIT 10
    ''', (brand,))
    results = cursor.fetchall()
    conn.close()
    return results


def get_cars_by_type(car_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT brand, model, price FROM cars
        WHERE type = ?
        ORDER BY price ASC LIMIT 10
    ''', (car_type,))
    results = cursor.fetchall()
    conn.close()
    return results

def compare_cars(model1, model2):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM cars
        WHERE model LIKE ? OR model LIKE ?
        ORDER BY brand ASC
        LIMIT 2
    ''', (f"%{model1}%", f"%{model2}%"))
    results = cursor.fetchall()
    conn.close()
    return results

def get_trade_in_estimate(brand, year, mileage):
    base_value = 20000
    age = 2025 - int(year)
    depreciation = age * 1000 + (int(mileage) // 10000) * 500
    estimated_value = max(2000, base_value - depreciation)
    return estimated_value

def get_dealers_by_brand(brand):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, location, contact FROM dealers
        WHERE brand = ?
        ORDER BY name ASC
    ''', (brand,))
    results = cursor.fetchall()
    conn.close()
    return results

def save_user_preference(user_id, brand, car_type, budget, fuel_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM user_preferences WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute('''
            UPDATE user_preferences
            SET preferred_brand = ?, car_type = ?, budget = ?, fuel_type = ?
            WHERE user_id = ?
        ''', (brand, car_type, budget, fuel_type, user_id))
    else:
        cursor.execute('''
            INSERT INTO user_preferences (user_id, preferred_brand, car_type, budget, fuel_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, brand, car_type, budget, fuel_type))

    conn.commit()
    conn.close()

def get_user_preference(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT preferred_brand, car_type, budget, fuel_type
        FROM user_preferences
        WHERE user_id = ?
    ''', (user_id,))
    pref = cursor.fetchone()
    conn.close()
    return pref
