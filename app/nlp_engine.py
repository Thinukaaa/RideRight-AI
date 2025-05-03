import json
import re
import spacy

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Load intents
with open("data/intents.json", "r") as file:
    intents = json.load(file)["intents"]

# Define known entities
CAR_BRANDS = ["Toyota", "Honda", "Ford", "BMW", "Tesla", "Hyundai", "Nissan"]
CAR_TYPES = ["SUV", "Sedan", "Hatchback", "Truck"]
CAR_MODELS = ["Corolla", "Civic", "Escape", "Leaf", "X3", "Elantra", "Model 3"]

def extract_entities(text):
    doc = nlp(text)
    entities = {}

    # Named Entity Recognition (spaCy)
    for ent in doc.ents:
        if ent.label_ == "ORG" and ent.text in CAR_BRANDS:
            entities["brand"] = ent.text
        elif ent.label_ == "DATE" and "20" in ent.text:
            try:
                entities["year"] = int(re.search(r'20\d{2}', ent.text).group())
            except:
                pass
        elif ent.label_ == "CARDINAL":
            try:
                val = int(ent.text.replace(',', ''))
                if 1000 < val < 1000000:
                    entities["budget"] = val
                elif val < 100000:  # assume mileage
                    entities["mileage"] = val
            except:
                pass

    # Manual matching (for type/model fallback)
    for brand in CAR_BRANDS:
        if brand.lower() in text.lower():
            entities["brand"] = brand

    for ctype in CAR_TYPES:
        if ctype.lower() in text.lower():
            entities["type"] = ctype

    for model in CAR_MODELS:
        if model.lower() in text.lower():
            if "model" in entities:
                entities["model2"] = model
            else:
                entities["model"] = model

    return entities

def match_intent(text):
    text = text.lower()
    best_match = {"tag": "unknown", "responses": ["Sorry, I didn’t get that. Can you rephrase?"]}
    highest_score = 0

    synonyms = {
        "budget_filter": ["cheap", "affordable", "under", "below", "less than"],
        "car_recommendation": ["suggest", "recommend", "good car"],
        "thanks": ["thanks", "thank you", "ok", "cool", "cheers", "appreciate it"],
        "dealer_query": ["dealers", "showroom", "where to buy", "find dealer", "nearby dealer"],
        "compare_cars": ["compare", "difference between", "vs", "better car"],
        "greeting": ["hi", "hello", "hey", "good morning"]
    }

    for intent in intents:
        base_score = 0
        for pattern in intent["patterns"]:
            words = pattern.lower().split()
            score = sum(1 for word in words if word in text) / len(words)
            base_score = max(base_score, score)

        # Bonus score if synonym detected
        for syn_intent, syn_list in synonyms.items():
            if syn_intent == intent["tag"]:
                if any(syn in text for syn in syn_list):
                    base_score += 0.4

        if base_score > highest_score and base_score > 0.4:
            best_match = intent
            highest_score = base_score

    return best_match


def process_input(user_input):
    entities = extract_entities(user_input)
    intent = match_intent(user_input)

    # Priority override if car type is detected
    if "type" in entities:
        intent = {"tag": "car_type_query", "responses": ["Let me show you cars in that category."]}

    return {
        "intent": intent["tag"],
        "response": intent["responses"][0],
        "entities": entities,
        "text": user_input
    }
    if intent["tag"] == "unknown":
     with open("logs/unknown_queries.txt", "a", encoding="utf-8") as f:
        f.write(user_input.strip() + "\n")
