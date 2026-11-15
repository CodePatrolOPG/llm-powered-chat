import streamlit as st
from google import genai
from functions import get_secret
from google.genai import types

api_key = get_secret("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

temperature = st.sidebar.slider(
    label="Select the temperature",
    min_value=0.0,
    max_value=2.0,
    value=1.0
)

from functions import get_secret, reset_chat

if st.sidebar.button("Reset chat"):
    reset_chat()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if not st.session_state.chat_history:
    st.session_state.chat_history.append(("assistant", "Hi! How can I help you?"))

user_message = st.chat_input("Type your message...")

for role, message in st.session_state.chat_history:
    st.chat_message(role).write(message)

if user_message:
    st.chat_message("user").write(user_message)
    st.session_state.chat_history.append(("user", user_message))

    system_prompt = """
        You are a thoughtful, practical decision-making tutor who helps people figure out the right choice when they feel stuck or unsure.

        How to guide the user:
        1. Clarify first if needed: if key context is missing (their goal, constraints, timeline, or what they're afraid of losing), ask 1–2 focused questions before jumping to a verdict.
        2. Frame the decision: separate reversible choices from high-stakes/irreversible ones, and surface trade-offs (short-term comfort vs. long-term benefit, opportunity cost, hidden assumptions).
        3. Compare options concretely: outline the main paths with honest pros, cons, and likely second-order consequences.
        4. Give a clear takeaway: recommend what seems strongest *for their specific situation* and explain why, while respecting that the final call is theirs.

        Tone & boundaries:
        - Be calm, honest, and grounded—no empty motivational clichés, no lecturing, no flattery.
        - Keep responses structured and concise so the user can actually think clearly.
        - You are not a licensed doctor, therapist, lawyer, or financial advisor. For medical, legal, or crisis situations, state that limit clearly and advise consulting a qualified professional.
    """
    full_input = f"{system_prompt}\n\nUser message:\n\"\"\"{user_message}\"\"\""

    context = [
          *[
            {
                "role": "model" if role == "assistant" else "user",
                "parts": [{"text": msg}],
            }
            for role, msg in st.session_state.chat_history[:-1]
        ],
        {"role": "user", "parts": [{"text": full_input}]},
    ]
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=context,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=250,
        ),
    )
    assistant_reply = response.text

    st.chat_message("assistant").write(assistant_reply)
    st.session_state.chat_history.append(("assistant", assistant_reply))