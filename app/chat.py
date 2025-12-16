import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("API_KEY"))

SYSTEM_PROMPT = """
You are Chill Panda 🐼 — a calm, empathetic mental health companion.
You respond warmly, supportively, and safely.
You do NOT give medical advice.
If user expresses distress, respond with empathy and encouragement.
"""

def generate_ai_reply(user_message: str, language: str) -> str:
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()
