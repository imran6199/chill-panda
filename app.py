import streamlit as st
import requests
import os
from dotenv import load_dotenv
import uuid
import random

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

st.set_page_config(
    page_title="Chill Panda 🐼 - Mental Health Companion",
    page_icon="🐼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function for meditation suggestions
def generate_meditation_suggestion(user_input, ai_response):
    """Generate meditation suggestion based on conversation"""
    
    meditations = [
        "Try 5 minutes of deep breathing: Inhale for 4, hold for 4, exhale for 6.",
        "Take a mindful walk for 10 minutes, noticing 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste.",
        "Practice gratitude: Write down 3 things you're thankful for today.",
        "Body scan meditation: Focus on relaxing each part of your body from head to toe.",
        "Loving-kindness meditation: Send kind thoughts to yourself, loved ones, and all beings."
    ]
    
    # Trigger meditation based on keywords
    stress_keywords = ["stress", "anxious", "worried", "overwhelmed", "pressure"]
    if any(keyword in user_input.lower() for keyword in stress_keywords):
        return random.choice(meditations)
    
    return None

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{uuid.uuid4().hex[:8]}"
if "language" not in st.session_state:
    st.session_state.language = "en"

# Sidebar configuration
with st.sidebar:
    st.title("🐼 Chill Panda Settings")
    
    st.session_state.language = st.selectbox(
        "Language",
        ["en", "zh-CN", "zh-HK"],
        index=0
    )
    
    show_history = st.checkbox("Show conversation history", value=True)
    
    st.divider()
    
    # Session management
    st.subheader("Session Management")
    st.write(f"**Session ID:** {st.session_state.session_id[:8]}...")
    st.write(f"**User ID:** {st.session_state.user_id}")
    
    if st.button("New Session", type="secondary"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    
    if st.button("Clear Chat", type="secondary"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Meditation section
    st.subheader("Mindfulness Tools")
    show_meditation = st.checkbox("Show meditation suggestions", value=True)
    
    if st.button("💭 Quick Meditation"):
        st.info("Take a deep breath... Inhale for 4 seconds, hold for 4, exhale for 6. Repeat 5 times.")
    
    st.divider()
    
    # About section
    st.subheader("About")
    st.markdown("""
    **Chill Panda** is a mental health companion 
    that combines AI with wisdom from the book 
    *"The Chill Panda"* by Joseph Rodrick Law.
    
    Remember: This is not a substitute for 
    professional medical advice.
    """)

# Main chat interface
st.title("🐼 Chill Panda - Mental Health Companion")
st.caption("A compassionate AI companion combining modern AI with ancient wisdom")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="🐼"):
            st.markdown(message["content"])
            if message.get("meditation_suggestion"):
                with st.expander("🧘 Suggested Meditation"):
                    st.write(message["meditation_suggestion"])

# Chat input
if prompt := st.chat_input("How are you feeling today?"):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare API request
    url = f"{BACKEND_URL.rstrip('/')}/api/v1/chat"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": OPENAI_API_KEY
    }
    payload = {
        "session_id": st.session_state.session_id,
        "user_id": st.session_state.user_id,
        "input_text": prompt,
        "language": st.session_state.language
    }
    
    # Display assistant response
    with st.chat_message("assistant", avatar="🐼"):
        message_placeholder = st.empty()
        with st.spinner("Chill Panda is thinking..."):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_reply = result.get("reply", "")
                    
                    # Display response
                    message_placeholder.markdown(ai_reply)
                    
                    # Add meditation suggestion if enabled
                    if show_meditation:
                        meditation_suggestion = generate_meditation_suggestion(prompt, ai_reply)
                        if meditation_suggestion:
                            with st.expander("🧘 Suggested Practice"):
                                st.write(meditation_suggestion)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": ai_reply,
                                "meditation_suggestion": meditation_suggestion
                            })
                        else:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": ai_reply
                            })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": ai_reply
                        })
                        
                else:
                    error_msg = f"Error: Backend returned status {response.status_code}"
                    message_placeholder.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Connection error: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Conversation history in sidebar
if show_history and st.session_state.messages:
    with st.sidebar.expander("📜 Conversation History", expanded=False):
        for i, msg in enumerate(st.session_state.messages[-10:]):  # Show last 10 messages
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content'][:50]}...")
            else:
                st.markdown(f"**Panda:** {msg['content'][:50]}...")
            if i < len(st.session_state.messages[-10:]) - 1:
                st.divider()



# Footer
st.divider()
st.caption("""
⚠️ **Important Notice:** Chill Panda is an AI companion for general mental wellness. 
It is not a substitute for professional medical advice, diagnosis, or treatment. 
If you're experiencing a mental health crisis, please contact a healthcare professional 
or crisis hotline in your country.
""")