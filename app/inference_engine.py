from app.db_queries import (
    get_filtered_cars,
    get_cars_by_brand,
    get_cars_by_type,
    compare_cars,
    get_trade_in_estimate,
    get_dealers_by_brand,
    save_user_preference,
    get_user_preference
)

def format_car(car):
    brand = car[0] or "Unknown"
    model = car[1] or "Unknown"
    car_type = car[2] or "Unknown"
    price = car[3] or 0
    fuel = car[4] or "N/A"
    transmission = car[5] or "N/A"
    seats = car[6] or "N/A"

    return f"""
<details>
<summary>🚗 <b>{brand} {model}</b> — ${price:,.0f}</summary>
<ul>
  <li><b>Type:</b> {car_type}</li>
  <li><b>Fuel:</b> {fuel}</li>
  <li><b>Transmission:</b> {transmission}</li>
  <li><b>Seats:</b> {seats}</li>
</ul>
</details>
"""

def summarize_filters(filters):
    summary = []
    if filters.get("brand"):
        summary.append(f"brand = {filters['brand']}")
    if filters.get("car_type"):
        summary.append(f"type = {filters['car_type']}")
    if filters.get("fuel_type"):
        summary.append(f"fuel = {filters['fuel_type']}")
    if filters.get("transmission"):
        summary.append(f"transmission = {filters['transmission']}")
    if filters.get("seats"):
        summary.append(f"seats = {filters['seats']}")
    if filters.get("budget"):
        summary.append(f"price ≤ {filters['budget']}")
    if filters.get("min_budget"):
        summary.append(f"price ≥ {filters['min_budget']}")
    if filters.get("max_budget"):
        summary.append(f"price ≤ {filters['max_budget']}")
    return ", ".join(summary)

def relaxed_search(entities):
    filters = {
        "brand": entities.get("brand"),
        "car_type": entities.get("type"),
        "fuel_type": entities.get("fuel"),
        "transmission": entities.get("transmission"),
        "seats": entities.get("seats"),
        "budget": entities.get("budget"),
        "min_budget": entities.get("min_budget"),
        "max_budget": entities.get("max_budget")
    }
    results = get_filtered_cars(**filters)
    return results, filters

def get_response(intent_data):
    intent = intent_data["intent"]
    entities = intent_data.get("entities", {})
    user_input = intent_data.get("text", "")

    def as_car_cards(results, title=None, filters=None):
        return {
            "cards": [format_car(r) for r in results],
            "title": title,
            "filters": summarize_filters(filters or {}),
            "format": "grid"
        }

    if intent in ["budget_filter", "car_recommendation"] and any(k in entities for k in ["budget", "min_budget", "max_budget"]):
        results, used_filters = relaxed_search(entities)
        if results:
            return as_car_cards(results, "Cars under your budget", used_filters)
        return "I couldn’t find anything matching those price and feature filters. Want to try adjusting your criteria?"

    elif intent == "brand_query" and "brand" in entities:
        results, used_filters = relaxed_search(entities)
        if results:
            return as_car_cards(results, f"{entities['brand']} Cars", used_filters)
        return f"I couldn't find {entities['brand']} listings matching those filters right now. Try adjusting the price or type."

    elif intent == "car_type_query" and "type" in entities:
        results, used_filters = relaxed_search(entities)
        if results:
            return as_car_cards(results, f"{entities['type'].capitalize()} Cars", used_filters)
        return f"No {entities['type']}s available at the moment – want to try another type?"

    elif intent == "car_features_filter":
        results, used_filters = relaxed_search(entities)
        if results:
            return as_car_cards(results, "Cars with selected features", used_filters)
        return "I couldn’t find any cars matching those features. Want to adjust?"

    elif intent == "compare_cars" and "model" in entities and "model2" in entities:
        model1, model2 = entities["model"], entities["model2"]
        results = compare_cars(model1, model2)
        if results:
            return as_car_cards(results, f"Comparison: {model1} vs {model2}")
        return f"I couldn’t find enough info to compare {model1} and {model2}."

    elif intent == "trade_in_value" and "year" in entities and "mileage" in entities:
        year = entities["year"]
        mileage = entities["mileage"]
        estimate = get_trade_in_estimate("Unknown", year, mileage)
        return f"Based on that, I’d estimate your trade-in value around ${estimate}."

    elif intent == "dealer_query" and "brand" in entities:
        brand = entities["brand"]
        dealers = get_dealers_by_brand(brand)
        if dealers:
            return "\n".join(
                f"🏢 <b>{name}</b> — {location} (📞 {contact})"
                for name, location, contact in dealers
            )
        return f"I couldn't locate any {brand} dealers at the moment."

    elif intent == "save_preference":
        user_id = "demo_user"
        save_user_preference(
            user_id,
            entities.get("brand", "Any"),
            entities.get("type", "Any"),
            entities.get("budget", 0),
            entities.get("fuel", "Any")
        )
        return "I’ve saved your preferences. I’ll remember them for next time!"

    elif intent == "show_preferences":
        user_id = "demo_user"
        pref = get_user_preference(user_id)
        if pref:
            return f"""Here’s what I remember about your preferences:
• Brand: {pref[0]}
• Type: {pref[1]}
• Budget: ${pref[2]:,.0f}
• Fuel: {pref[3]}"""
        return "Looks like I don’t have anything saved for you yet!"

    elif intent in [
        "creator_info", "bot_identity", "wellbeing", "joke", "thanks", "goodbye",
        "unknown", "bot_capabilities", "repeat_request", "clarification",
        "emotion_positive", "emotion_negative"
    ]:
        return intent_data["response"]

    return intent_data['response']
