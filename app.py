# streamlit_app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv
import uuid
import time

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")  # set this in your .env (x-api-key for backend)

st.set_page_config(page_title="Chill Panda", page_icon="🐼", layout="wide")

st.sidebar.title("Chill Panda Settings")
lang_option = st.sidebar.selectbox("Language", ["en", "zh-CN", "zh-HK"])
show_meditation = st.sidebar.checkbox("Show meditation suggestions", value=True)

# Session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"assistant", "text": ...}
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("🐼 Chill Panda")

# Show messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['text']}")
    else:
        st.markdown(f"**🐼 Chill Panda:** {msg['text']}")

# Input
# Use a different key to avoid modifying session_state directly
user_input = st.text_input("Type a message...", key="user_input")
send = st.button("Send")


def call_backend(session_id, user_id, text, language):
    url = BACKEND_URL.rstrip("/") + "/api/v1/chat"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    payload = {
        "session_id": session_id,
        "user_id": user_id,
        "input_text": text,
        "language": language
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
    except Exception as e:
        return {"error": f"Request failed: {e}"}
    return {"status_code": resp.status_code, "text": resp.text, "json": (resp.json() if resp.ok else None)}


if send and user_input.strip():
    # Append user message
    st.session_state.messages.append({"role": "user", "text": user_input})

    # Call backend
    debug_result = call_backend(st.session_state.session_id, "streamlit_user", user_input, lang_option)

    # If network/request error
    if debug_result.get("error"):
        st.session_state.messages.append({"role": "assistant", "text": "🐼 Chill Panda: Error communicating with backend."})
        st.error(debug_result["error"])
    else:
        code = debug_result["status_code"]
        if code != 200:
            # Show details so you can debug easily
            st.session_state.messages.append({"role": "assistant", "text": "🐼 Chill Panda: Error communicating with backend."})
            st.error(f"Backend returned status {code}")
            st.text("Response text:")
            st.text(debug_result["text"])
        else:
            # Success: parse JSON response
            body = debug_result["json"]
            reply_text = body.get("reply", "No reply field in response.")
            st.session_state.messages.append({"role": "assistant", "text": reply_text})

            # Optionally show meditation
            if show_meditation and body.get("recommended_meditation"):
                st.info(f"🧘 Meditation suggested: {body['recommended_meditation']}")

    # No need to manually clear st.session_state["input_box"]
    # Streamlit will handle input automatically
    time.sleep(0.1)
