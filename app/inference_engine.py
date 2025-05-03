from app.db_queries import (
    get_cars_by_budget,
    get_cars_by_brand,
    get_cars_by_type,
    compare_cars,
    get_trade_in_estimate,
    get_dealers_by_brand,
    save_user_preference,
    get_user_preference
)

def get_response(intent_data):
    intent = intent_data["intent"]
    entities = intent_data.get("entities", {})
    user_input = intent_data.get("text", "")

    # 1. Budget-based car recommendations
    if intent == "budget_filter" or (intent == "car_recommendation" and "budget" in entities):
        budget = entities.get("budget")
        if budget:
            results = get_cars_by_budget(budget)
            if results:
                return "Here are some great picks under your budget:\n" + "\n".join(
                    [f"{brand} {model} - ${price}" for brand, model, price in results])
            else:
                return "I couldn’t find anything under that price. Want to expand your range a little?"
        return "Got a budget in mind? I’ll work within it."

    # 2. Brand-based car lookup
    elif intent == "brand_query" and "brand" in entities:
        brand = entities["brand"]
        results = get_cars_by_brand(brand)
        if results:
            return f"Here are some {brand} models worth checking out:\n" + "\n".join(
                [f"{brand} {model} ({type}) - ${price}" for model, type, price in results])
        return f"I couldn't find {brand} listings right now. Maybe try a different brand?"

    # 3. Type-based car recommendations
    elif intent == "car_type_query" and "type" in entities:
        car_type = entities["type"]
        results = get_cars_by_type(car_type)
        if results:
            return f"Here’s what I found in the {car_type} category:\n" + "\n".join(
                [f"{brand} {model} - ${price}" for brand, model, price in results])
        return f"No {car_type}s available at the moment – want to try another type?"

    # 4. Compare cars
    elif intent == "compare_cars" and "model" in entities and "model2" in entities:
        model1, model2 = entities["model"], entities["model2"]
        results = compare_cars(model1, model2)
        if results:
            return f"Here’s a quick side-by-side for {model1} and {model2}:\n" + "\n".join(
                [f"{brand} {model} ({type}) - ${price}, {fuel_type}, {mileage} MPG"
                 for (_, brand, model, type, price, fuel_type, mileage, _, _, _, _) in results])
        return f"I couldn’t find enough info to compare those models right now."

    # 5. Trade-in evaluation
    elif intent == "trade_in_value" and "year" in entities and "mileage" in entities:
        year = entities["year"]
        mileage = entities["mileage"]
        estimate = get_trade_in_estimate("Unknown", year, mileage)
        return f"Based on that, I’d estimate your trade-in value around ${estimate}."

    # 6. Dealer query
    elif intent == "dealer_query" and "brand" in entities:
        brand = entities["brand"]
        dealers = get_dealers_by_brand(brand)
        if dealers:
            return f"Here are some {brand} dealers I found:\n" + "\n".join(
                [f"{name} ({location}) – Contact: {contact}" for name, location, contact in dealers])
        return f"I couldn't locate any {brand} dealers at the moment."

    # 7. Save user preferences
    elif intent == "save_preference":
        user_id = "demo_user"
        brand = entities.get("brand", "Any")
        car_type = entities.get("type", "Any")
        budget = entities.get("budget", 0)
        fuel = entities.get("fuel", "Any")
        save_user_preference(user_id, brand, car_type, budget, fuel)
        return f"I’ve saved your preferences for {car_type}s from {brand} under ${budget}. Got it!"

    # 8. Recall user preferences
    elif intent == "show_preferences":
        user_id = "demo_user"
        pref = get_user_preference(user_id)
        if pref:
            return f"Here’s what I remember about your preferences:\nBrand: {pref[0]}, Type: {pref[1]}, Budget: ${pref[2]}, Fuel: {pref[3]}"
        return "Looks like I don’t have anything saved for you yet!"

    # 9. Car recommendation based on saved preferences
    elif intent == "car_recommendation":
        user_id = "demo_user"
        pref = get_user_preference(user_id)
        if pref:
            brand, car_type, budget, fuel = pref
            cars = get_cars_by_brand(brand)
            cars = [car for car in cars if car_type.lower() in car[1].lower() and car[2] <= budget]
            if cars:
                return f"Based on what you like, here are some {car_type}s from {brand}:\n" + "\n".join(
                    [f"{brand} {model} - ${price}" for model, _, price in cars])
            return "I looked through your preferences, but nothing matched. Maybe tweak the budget or car type?"

    # Default response (unknown intent or small talk)
    return f"{intent_data['response']} (Let me know if you'd like help choosing a car!)"
