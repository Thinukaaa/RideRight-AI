import json
import os

LOG_PATH = "logs/unknown_queries.txt"
INTENTS_PATH = "data/intents.json"

def train_from_logs():
    if not os.path.exists(LOG_PATH):
        print("No unknown queries found.")
        return

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        unknown_queries = list(set(line.strip() for line in f if line.strip()))

    if not unknown_queries:
        print("No new unknown queries to process.")
        return

    # Load existing intents
    with open(INTENTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("🧠 TRAINING MODE — Assign intent tags to the following unknown queries:\n")
    for query in unknown_queries:
        print(f"\nQuery: {query}")
        tag = input("→ What intent should this be? (e.g. car_recommendation, thanks, etc): ").strip()
        response = input("→ Bot response for this query: ").strip()

        # Check if tag exists
        for intent in data["intents"]:
            if intent["tag"] == tag:
                intent["patterns"].append(query)
                if response not in intent["responses"]:
                    intent["responses"].append(response)
                break
        else:
            # Create new intent if tag doesn't exist
            data["intents"].append({
                "tag": tag,
                "patterns": [query],
                "responses": [response]
            })

    # Save updated intents
    with open(INTENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Clear log after training
    open(LOG_PATH, "w", encoding="utf-8").close()

    print("\n✅ Training complete! New queries have been added to your intents.")

if __name__ == "__main__":
    train_from_logs()
