"""
Advanced AI Interview Chatbot (ChatGPT Style + Smart Page Suggestions)
"""

import streamlit as st
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

# -----------------------------
# APP PAGE CONTEXT (IMPORTANT)
# -----------------------------
APP_PAGES = {
    "dashboard": "Overview of performance, stats, and activity",
    "profile": "User profile and settings",
    "resume_analyzer": "AI resume analysis and feedback",
    "technical_interview": "Technical DSA / coding interview practice",
    "coding_interview": "Live coding rounds and problems",
    "non_technical": "Communication and behavioral practice",
    "hr_interview": "HR interview questions and answers",
    "aptitude_test": "Quantitative aptitude practice tests",
    "voice_interview": "Voice-based interview practice",
    "company_prep": "Company-specific interview preparation",
    "analytics": "Performance analytics and progress tracking",
    "reports": "Detailed reports and evaluation history",
    "chatbot": "AI interview assistant chatbot"
}


# -----------------------------
# SYSTEM MODES
# -----------------------------
MODES = {
    "💬 General": "You are a helpful AI assistant for interview preparation.",

    "💻 Technical": """
You are a technical interview expert.
Ask and answer DSA, Python, Java, SQL, AI, System Design questions.
Keep answers structured and interview focused.
""",

    "🤝 HR": """
You are an HR interviewer.
Ask behavioral questions, communication, leadership, teamwork questions.
Also give model answers.
""",

    "🧠 Question Generator": """
You generate high-quality interview questions.
If user gives a topic, generate 10–15 interview questions with difficulty levels.
""",

    "🎯 Mock Interview": """
You are a strict interviewer.
Ask ONE question at a time.
Wait for user answer.
Then evaluate answer and give score out of 10.
Then ask next question.
"""
}


# -----------------------------
# GROQ RESPONSE
# -----------------------------
def get_response(messages):
    return client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.7,
    ).choices[0].message.content


# -----------------------------
# SIMPLE RULE-BASED PAGE SUGGESTION
# -----------------------------
def get_relevant_page(user_input):
    text = user_input.lower()

    if "resume" in text:
        return "resume_analyzer"
    elif "code" in text or "coding" in text or "dsa" in text:
        return "coding_interview"
    elif "technical" in text or "python" in text or "java" in text:
        return "technical_interview"
    elif "hr" in text or "behavior" in text:
        return "hr_interview"
    elif "aptitude" in text or "math" in text:
        return "aptitude_test"
    elif "voice" in text:
        return "voice_interview"
    elif "company" in text:
        return "company_prep"
    else:
        return None


# -----------------------------
# MAIN CHATBOT UI
# -----------------------------
def show_chatbot(user=None):

    st.title("🤖 AI Interview Chatbot (Pro Mode)")

    # Mode selector
    mode = st.selectbox("Select Mode", list(MODES.keys()))

    # -----------------------------
    # SYSTEM PROMPT (SMART + CONTROLLED)
    # -----------------------------
    system_prompt = f"""
You are an AI Interview Assistant chatbot.

You help users with interview preparation AND guide them to relevant sections of the app.

AVAILABLE APP SECTIONS:
{APP_PAGES}

RULES:
- Be helpful and concise.
- If relevant, suggest ONLY 1 or 2 best matching sections.
- Do NOT list all pages.
- Always explain WHY you suggest a section.
- If not relevant, do not suggest navigation.
"""

    # -----------------------------
    # SESSION STATE
    # -----------------------------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # -----------------------------
    # USER INPUT
    # -----------------------------
    user_input = st.chat_input("Ask anything...")

    if user_input:

        # store user message
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        # rule-based suggestion (extra safety layer)
        suggested_page = get_relevant_page(user_input)

        # build messages
        messages = [
            {"role": "system", "content": system_prompt}
        ] + st.session_state.chat_history

        response = get_response(messages)

        # append AI response
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )

        # show suggestion (UI helper)
        if suggested_page:
            st.info(
                f"💡 Suggested Section: **{suggested_page.replace('_', ' ').title()}**"
            )

    # -----------------------------
    # DISPLAY CHAT
    # -----------------------------
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"🧑‍💻 **You:** {msg['content']}")
        else:
            st.markdown(f"🤖 **AI:** {msg['content']}")

    # -----------------------------
    # CLEAR CHAT
    # -----------------------------
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()