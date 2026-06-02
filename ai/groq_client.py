"""
Groq API Client - AI model integration
"""

import streamlit as st
from groq import Groq
import logging
import time

logger = logging.getLogger(__name__)


# -----------------------------
# CONFIG (NO config.py USED)
# -----------------------------
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MAX_TOKENS = 2048
GROQ_TEMPERATURE = 0.7


@st.cache_resource
def get_groq_client() -> Groq:
    """Get cached Groq client instance."""

    api_key = st.secrets.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError("Groq API key not configured in Streamlit secrets.")

    return Groq(api_key=api_key)


# -----------------------------
# CHAT COMPLETION
# -----------------------------
def chat_completion(
    messages: list,
    model: str = None,
    max_tokens: int = None,
    temperature: float = None,
    system_prompt: str = None,
) -> str:

    try:
        client = get_groq_client()

        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})

        all_messages.extend(messages)

        response = client.chat.completions.create(
            model=model or GROQ_MODEL,
            messages=all_messages,
            max_tokens=max_tokens or GROQ_MAX_TOKENS,
            temperature=temperature or GROQ_TEMPERATURE,
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Groq API error: {e}")
        raise


# -----------------------------
# RETRY LOGIC
# -----------------------------
def generate_with_retry(messages: list, max_retries: int = 3, **kwargs) -> str:

    for attempt in range(max_retries):
        try:
            return chat_completion(messages, **kwargs)

        except Exception as e:
            if attempt == max_retries - 1:
                raise

            wait_time = 2 ** attempt
            logger.warning(f"Retry {attempt+1} failed: {e}")
            time.sleep(wait_time)


# -----------------------------
# STREAMING RESPONSE
# -----------------------------
def stream_completion(messages: list, system_prompt: str = None, **kwargs):

    try:
        client = get_groq_client()

        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})

        all_messages.extend(messages)

        stream = client.chat.completions.create(
            model=kwargs.get("model", GROQ_MODEL),
            messages=all_messages,
            max_tokens=kwargs.get("max_tokens", GROQ_MAX_TOKENS),
            temperature=kwargs.get("temperature", GROQ_TEMPERATURE),
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        logger.error(f"Groq streaming error: {e}")
        raise