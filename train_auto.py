import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

LOG_PATH = "logs/unknown_queries.txt"
INTENTS_PATH = "data/intents.json"
CONFIDENCE_THRESHOLD = 0.75

def load_data():
    with open(INTENTS_PATH, "r", encoding="utf-8") as f:
        intents_data = json.load(f)["intents"]

    patterns = []
    tags = []

    for intent in intents_data:
        for pattern in intent["patterns"]:
            patterns.append(pattern)
            tags.append(intent["tag"])

    return patterns, tags, intents_data

def train_auto():
    if not os.path.exists(LOG_PATH):
        print("No unknown queries to train.")
        return

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        unknowns = list(set(line.strip() for line in f if line.strip()))

    if not unknowns:
        print("No unknowns to process.")
        return

    patterns, tags, intents_data = load_data()

    vectorizer = TfidfVectorizer().fit(patterns + unknowns)
    known_vectors = vectorizer.transform(patterns)
    unknown_vectors = vectorizer.transform(unknowns)

    unsure = []

    for i, unknown in enumerate(unknowns):
        sim = cosine_similarity(unknown_vectors[i], known_vectors)
        best_match_idx = sim.argmax()
        best_score = sim[0, best_match_idx]

        if best_score >= CONFIDENCE_THRESHOLD:
            predicted_tag = tags[best_match_idx]
            matched_pattern = patterns[best_match_idx]

            # Add this unknown to that tag
            for intent in intents_data:
                if intent["tag"] == predicted_tag:
                    if unknown not in intent["patterns"]:
                        intent["patterns"].append(unknown)
                    break

            print(f"✅ {unknown} → {predicted_tag} (matched: '{matched_pattern}', score: {best_score:.2f})")
        else:
            unsure.append((unknown, best_score))
            print(f"❓ Could not confidently assign intent for: '{unknown}' (score: {best_score:.2f})")

    # Save updated intents
    with open(INTENTS_PATH, "w", encoding="utf-8") as f:
        json.dump({"intents": intents_data}, f, indent=2)

    # Clear log
    open(LOG_PATH, "w", encoding="utf-8").close()

    # Save unsure to separate file
    if unsure:
        with open("logs/manual_review.txt", "w", encoding="utf-8") as f:
            for query, score in unsure:
                f.write(f"{query} | score: {score:.2f}\n")

        print("\n⚠️ Some queries were not confidently matched and saved to logs/manual_review.txt.")

if __name__ == "__main__":
    train_auto()
