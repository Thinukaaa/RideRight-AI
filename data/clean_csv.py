import pandas as pd

# Load raw CSV
df = pd.read_csv("data/raw_car_data.csv")

# Split 'name' into brand and model
df[['brand', 'model']] = df['name'].str.split(' ', n=1, expand=True)



# Build cleaned DataFrame
cleaned_df = pd.DataFrame({
    "brand": df['brand'],
    "model": df['model'].fillna("Unknown"),
    "type": "Unknown",  # Optional: add detection later
    "price": df['selling_price'],
    "fuel_type": df['fuel'],
    "mileage": df['km_driven'],
    "year": df['year'],
    "transmission": df['transmission'],
    "seats": df['seats'].fillna(5).astype(int)
})

# Save to new file
cleaned_df.to_csv("data/car_inventory_clean.csv", index=False)
print("✅ Cleaned car inventory saved to 'car_inventory_clean.csv'")
