from app.nlp_engine import process_input
from app.inference_engine import get_response
from datetime import datetime

def log_conversation(user_input, reply):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] User: {user_input}\n[{timestamp}] Raya: {reply}\n\n"
    
    with open("logs/conversation_log.txt", "a", encoding="utf-8") as f:
        f.write(log_line)

def start_chat():
    print("🚗 RideRight AI – Powered by Raya")
    print("💬 How can I help you find your perfect ride today?\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            goodbye_msg = "Thanks for chatting with me today! 🚘 Wishing you smooth drives and smart buys!"
            print(f"Raya: {goodbye_msg}")
            log_conversation(user_input, goodbye_msg)
            break

        intent_data = process_input(user_input)
        intent_data["text"] = user_input
        reply = get_response(intent_data)

        print(f"Raya: {reply}")
        log_conversation(user_input, reply)
