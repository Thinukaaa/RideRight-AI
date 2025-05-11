import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

LOG_PATH = "logs/unknown_queries.txt"
INTENTS_PATH = "data/intents.json"
REVIEW_PATH = "logs/manual_review.txt"
CONFIDENCE_THRESHOLD = 0.5  # suggest if above 50%

def load_intents():
    with open(INTENTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    patterns = []
    tags = []
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            patterns.append(pattern)
            tags.append(intent["tag"])
    return patterns, tags, data

def train_semi_auto():
    if not os.path.exists(LOG_PATH):
        print("❌ No unknown queries logged.")
        return

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        unknowns = list(set(line.strip() for line in f if line.strip()))

    if not unknowns:
        print("✅ No unknowns to process.")
        return

    patterns, tags, intents_data = load_intents()
    vectorizer = TfidfVectorizer().fit(patterns + unknowns)
    known_vectors = vectorizer.transform(patterns)
    unknown_vectors = vectorizer.transform(unknowns)

    manual_review = []

    for i, unknown in enumerate(unknowns):
        sim = cosine_similarity(unknown_vectors[i], known_vectors)
        best_idx = sim.argmax()
        best_score = sim[0, best_idx]
        predicted_tag = tags[best_idx]
        matched_pattern = patterns[best_idx]

        print("\n🧠 New query:", unknown)
        print(f"🔍 Suggested intent: {predicted_tag} (matched: '{matched_pattern}' | score: {best_score:.2f})")

        if best_score >= CONFIDENCE_THRESHOLD:
            action = input("✅ Accept this intent? (Y to accept / N to assign manually / S to skip): ").strip().lower()
            if action == "y":
                # Add pattern to existing intent
                for intent in intents_data["intents"]:
                    if intent["tag"] == predicted_tag:
                        intent["patterns"].append(unknown)
                        break
            elif action == "n":
                new_tag = input("✏️ Enter the correct intent tag: ").strip()
                new_response = input("💬 Enter a response for this intent: ").strip()
                for intent in intents_data["intents"]:
                    if intent["tag"] == new_tag:
                        intent["patterns"].append(unknown)
                        if new_response not in intent["responses"]:
                            intent["responses"].append(new_response)
                        break
                else:
                    intents_data["intents"].append({
                        "tag": new_tag,
                        "patterns": [unknown],
                        "responses": [new_response]
                    })
            else:
                manual_review.append((unknown, best_score))
        else:
            manual_review.append((unknown, best_score))
            print("⚠️ Score too low for auto-matching. Added to manual review.")

    # Save updated intents
    with open(INTENTS_PATH, "w", encoding="utf-8") as f:
        json.dump({"intents": intents_data["intents"]}, f, indent=2)

    # Clear unknowns
    open(LOG_PATH, "w", encoding="utf-8").close()

    # Save unsure entries
    if manual_review:
        with open(REVIEW_PATH, "w", encoding="utf-8") as f:
            for query, score in manual_review:
                f.write(f"{query} | score: {score:.2f}\n")
        print(f"\n📝 {len(manual_review)} items saved to manual_review.txt for further review.")

    print("\n✅ Semi-auto training complete!")

if __name__ == "__main__":
    train_semi_auto()
