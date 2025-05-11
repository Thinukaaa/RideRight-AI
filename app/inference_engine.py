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
    # No longer used in UI title
    summary = []
    if filters.get("brand"):
        summary.append(f"{filters['brand']}")
    if filters.get("car_type"):
        summary.append(f"{filters['car_type']}")
    if filters.get("fuel_type"):
        summary.append(f"{filters['fuel_type']}")
    if filters.get("transmission"):
        summary.append(f"{filters['transmission']}")
    if filters.get("seats"):
        summary.append(f"{filters['seats']} seats")
    if filters.get("budget"):
        summary.append(f"≤ ${filters['budget']}")
    if filters.get("min_budget"):
        summary.append(f"≥ ${filters['min_budget']}")
    if filters.get("max_budget"):
        summary.append(f"≤ ${filters['max_budget']}")
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

    def as_car_cards(results, title=None):
        return {
            "cards": [format_car(r) for r in results],
            "title": title or "Matching Cars",
            "format": "grid"
        }

    if intent in ["budget_filter", "car_recommendation"] and any(k in entities for k in ["budget", "min_budget", "max_budget"]):
        results, _ = relaxed_search(entities)
        if results:
            return as_car_cards(results, "Matching Cars")
        return "No cars matched that request. Want to try relaxing your filters?"

    elif intent == "brand_query" and "brand" in entities:
        results, _ = relaxed_search(entities)
        if results:
            return as_car_cards(results, f"{entities['brand']} Cars")
        return f"I couldn't find any {entities['brand']} cars matching your criteria."

    elif intent == "car_type_query" and "type" in entities:
        results = get_cars_by_type(entities["type"])
        if results:
            formatted = [(brand, model, entities["type"], price, None, None, None) for brand, model, price in results]
            return as_car_cards(formatted, f"{entities['type'].capitalize()} Cars")
        return f"No {entities['type']}s available at the moment – want to try another type?"

    elif intent == "compare_cars" and all(k in entities for k in ["model", "model2"]):
        model1, model2 = entities["model"], entities["model2"]
        results = compare_cars(model1, model2)
        if results:
            return as_car_cards(results, f"{model1} vs {model2}")
        return f"I couldn’t find enough info to compare {model1} and {model2}."

    elif intent == "trade_in_value" and "year" in entities and "mileage" in entities:
        estimate = get_trade_in_estimate("Unknown", entities["year"], entities["mileage"])
        return f"Based on that, I’d estimate your trade-in value around ${estimate:,}."

    elif intent == "dealer_query" and "brand" in entities:
        brand = entities["brand"]
        dealers = get_dealers_by_brand(brand)
        if dealers:
            return "\n".join(
                f"🏢 <b>{name}</b> — {location} (📞 {contact})"
                for name, location, contact in dealers
            )
        return f"No dealers found for {brand}."

    elif intent == "save_preference":
        user_id = "demo_user"
        save_user_preference(
            user_id,
            entities.get("brand", "Any"),
            entities.get("type", "Any"),
            entities.get("budget", 0),
            entities.get("fuel", "Any")
        )
        return "Your preferences have been saved. I'll use them to personalize future recommendations."

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

    # Static intent fallback handler
    elif intent in [
        "creator_info", "bot_identity", "wellbeing", "joke", "thanks", "goodbye",
        "unknown", "bot_capabilities", "repeat_request", "clarification",
        "emotion_positive", "emotion_negative"
    ]:
        return intent_data["response"]

    return intent_data["response"]
