import streamlit as st
from app.nlp_engine import process_input
from app.inference_engine import get_response
from streamlit_extras.stylable_container import stylable_container

# --- Session Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "context" not in st.session_state:
    st.session_state.context = {}

# --- Page Config ---
st.set_page_config(page_title="Raya – RideRight AI", page_icon="🚗", layout="centered")

# --- Custom Styles ---
st.markdown("""
<style>
body {
    background-color: #0D0D0D;
    color: #F1F1F1;
    font-family: 'Segoe UI', sans-serif;
}
.chat-bubble {
    padding: 10px 15px;
    margin: 10px 0;
    border-radius: 15px;
    max-width: 80%;
    font-size: 16px;
    line-height: 1.4;
}
.user-bubble {
    background-color: #1E1E1E;
    color: #FFD369;
    align-self: flex-end;
    text-align: right;
}
.bot-bubble {
    background-color: #222831;
    color: #EEEEEE;
    border-left: 5px solid #00ADB5;
}
.card-box {
    border: 1px solid #444;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 10px;
    background-color: #333;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("### 🤖 Raya – Your Futuristic Auto Sales Assistant")
st.caption("Ask me anything car-related — I'm here to help you choose the best Ride for you!")

# --- Chat Display ---
with st.container():
    for speaker, message in st.session_state.chat_history:
        if speaker == "You":
            st.markdown(f"<div class='chat-bubble user-bubble'>🧑‍💼 {message}</div>", unsafe_allow_html=True)

        elif isinstance(message, dict) and message.get("format") == "grid":
            st.markdown(f"**{message['title']}**")
            cars = message["cards"]
            num_cols = 2 if len(cars) < 4 else 3
            cols = st.columns(num_cols)
            for i, car in enumerate(cars):
                with cols[i % num_cols]:
                    st.markdown(f"<div class='card-box'>{car}</div>", unsafe_allow_html=True)

        else:
            st.markdown(f"<div class='chat-bubble bot-bubble'>🤖 {message}</div>", unsafe_allow_html=True)

# --- Input Box ---
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Type your message:",
        placeholder="E.g., Show me electric SUVs under 30k",
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("Send 🚀")

# --- Process Submission ---
if submitted and user_input.strip():
    intent_data = process_input(user_input.strip())

    # Use prior context if needed
    for key in ["brand", "type", "fuel", "budget", "min_budget", "max_budget"]:
        if key not in intent_data["entities"] and key in st.session_state.context:
            intent_data["entities"][key] = st.session_state.context[key]

    # Save context
    st.session_state.context.update(intent_data["entities"])
    intent_data["text"] = user_input.strip()

    reply = get_response(intent_data)

    # Append to chat history
    st.session_state.chat_history.append(("You", user_input.strip()))
    st.session_state.chat_history.append(("Raya", reply))
