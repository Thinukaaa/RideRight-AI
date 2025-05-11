import json
import re
import spacy
import difflib
import streamlit as st

nlp = spacy.load("en_core_web_sm")

with open("data/intents.json", "r", encoding="utf-8") as file:
    intents = json.load(file)["intents"]

CAR_BRANDS = ["Toyota", "Honda", "Ford", "BMW", "Tesla", "Hyundai", "Nissan", "Chevrolet", "Kia"]
CAR_TYPES = ["SUV", "Sedan", "Hatchback", "Truck", "Coupe", "Convertible"]
FUEL_TYPES = ["petrol", "diesel", "electric", "hybrid"]
TRANSMISSIONS = ["manual", "automatic", "auto"]
SEATING_PATTERNS = [r"(\d)[ -]?seater", r"seating for (\d+)", r"(\d)\s?seats"]

TYPE_SYNONYMS = {
    "sedan": ["sedan", "saloon"],
    "hatchback": ["hatchback", "compact"],
    "suv": ["suv", "jeep", "4x4"]
}

def fuzzy_match(word, options, cutoff=0.75):
    matches = difflib.get_close_matches(word.lower(), [opt.lower() for opt in options], n=1, cutoff=cutoff)
    if matches:
        return next((opt for opt in options if opt.lower() == matches[0]), None)
    return None

def extract_entities(text):
    doc = nlp(text)
    text_lower = text.lower()
    entities = {}

    if "under" in text_lower or "less than" in text_lower:
        match = re.search(r"(\d{1,3})(k|K)", text_lower)
        if match:
            entities["max_budget"] = int(match.group(1)) * 1000
    elif "over" in text_lower or "more than" in text_lower:
        match = re.search(r"(\d{1,3})(k|K)", text_lower)
        if match:
            entities["min_budget"] = int(match.group(1)) * 1000

    for ent in doc.ents:
        if ent.label_ == "ORG":
            brand = fuzzy_match(ent.text, CAR_BRANDS)
            if brand:
                entities["brand"] = brand
        elif ent.label_ == "CARDINAL":
            try:
                val = int(ent.text.replace(",", ""))
                if "under" in text_lower or "less than" in text_lower:
                    entities["max_budget"] = val
                elif "over" in text_lower or "more than" in text_lower:
                    entities["min_budget"] = val
                elif 10000 < val < 10000000:
                    entities["budget"] = val
                elif val < 100000:
                    entities["mileage"] = val
            except:
                pass
        elif ent.label_ == "DATE" and "20" in ent.text:
            match = re.search(r'20\d{2}', ent.text)
            if match:
                entities["year"] = int(match.group())

    for word in text_lower.split():
        if "brand" not in entities:
            match = fuzzy_match(word, CAR_BRANDS)
            if match:
                entities["brand"] = match

    for formal, synonyms in TYPE_SYNONYMS.items():
        if any(syn in text_lower for syn in synonyms):
            entities["type"] = formal.lower()

    for fuel in FUEL_TYPES:
        if fuel in text_lower:
            entities["fuel"] = fuel

    for trans in TRANSMISSIONS:
        if trans in text_lower:
            entities["transmission"] = "automatic" if "auto" in trans else trans

    for pattern in SEATING_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            try:
                entities["seats"] = int(match.group(1))
            except:
                continue

    return entities

def match_intent(text):
    text = text.lower()
    best_match = {"tag": "unknown", "responses": ["Sorry, I didn’t get that. Can you rephrase?"]}
    highest_score = 0

    synonyms = {
        "budget_filter": ["cheap", "affordable", "under", "less than", "over", "more than", "cost"],
        "car_recommendation": ["recommend", "suggest", "what car", "good car", "show cars", "need a car"],
        "thanks": ["thanks", "thank you", "ok", "cool", "cheers"],
        "dealer_query": ["dealer", "where to buy", "showroom"],
        "compare_cars": ["compare", "versus", "vs", "difference"],
        "greeting": ["hi", "hello", "hey", "good morning"]
    }

    for intent in intents:
        for pattern in intent["patterns"]:
            score = sum(1 for word in pattern.lower().split() if word in text) / len(pattern.split())
            if score > highest_score and score > 0.4:
                best_match = intent
                highest_score = score

        for syn_intent, syn_list in synonyms.items():
            if syn_intent == intent["tag"] and any(word in text for word in syn_list):
                highest_score += 0.3
                best_match = intent

    return best_match

def process_input(user_input):
    entities = extract_entities(user_input)

    if "chat_context" not in st.session_state:
        st.session_state.chat_context = {}

    for key in ["brand", "type", "fuel", "budget", "max_budget", "min_budget"]:
        if key not in entities and key in st.session_state.chat_context:
            entities[key] = st.session_state.chat_context[key]

    for key in ["brand", "type", "fuel", "budget", "max_budget", "min_budget"]:
        if key in entities:
            st.session_state.chat_context[key] = entities[key]

    intent = match_intent(user_input)
    intent = match_intent(user_input)

# Smart override logic
    if "brand" in entities:
        intent = {"tag": "brand_query", "responses": ["Here are some models from that brand:"]}
    elif "type" in entities:
        intent = {"tag": "car_type_query", "responses": ["Looking up cars in that category..."]}
    elif "fuel" in entities or "transmission" in entities or "seats" in entities:
        intent = {"tag": "car_features_filter", "responses": ["Let me find cars that match those features..."]}

    return {
        "intent": intent["tag"],
        "response": intent["responses"][0],
        "entities": entities,
        "text": user_input
    }
