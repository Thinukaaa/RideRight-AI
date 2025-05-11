from app.db_queries import *

print("Cars under $30000:")
for car in get_cars_by_budget(30000):
    print(car)

print("\nCars by brand Honda:")
for car in get_cars_by_brand("Honda"):
    print(car)

print("\nCompare Civic and Corolla:")
for car in compare_cars("Civic", "Corolla"):
    print(car)

print("\nEstimated Trade-in Value:")
print(get_trade_in_estimate("Yaris", 2016, 85000))

print("\nDealers for Toyota:")
for dealer in get_dealers_by_brand("Toyota"):
    print(dealer)
