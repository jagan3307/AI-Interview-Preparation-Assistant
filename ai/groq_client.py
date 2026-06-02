"""
Groq API Client - AI model integration
"""

import streamlit as st
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_TOKENS, GROQ_TEMPERATURE
import logging
import time

logger = logging.getLogger(__name__)


@st.cache_resource
def get_groq_client() -> Groq:
    """Get cached Groq client instance."""
    if not GROQ_API_KEY:
        raise ValueError(
            "Groq API key not configured. "
            "Please set GROQ_API_KEY in your .env file."
        )
    return Groq(api_key=GROQ_API_KEY)


def chat_completion(
    messages: list,
    model: str = None,
    max_tokens: int = None,
    temperature: float = None,
    system_prompt: str = None,
) -> str:
    """
    Generate a chat completion using Groq API.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model to use (defaults to config)
        max_tokens: Max tokens in response
        temperature: Temperature for generation
        system_prompt: Optional system prompt to prepend
    
    Returns:
        Generated text response
    """
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


def generate_with_retry(messages: list, max_retries: int = 3, **kwargs) -> str:
    """Generate completion with retry logic."""
    for attempt in range(max_retries):
        try:
            return chat_completion(messages, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
            time.sleep(wait_time)


def stream_completion(messages: list, system_prompt: str = None, **kwargs):
    """
    Stream a chat completion (for real-time display).
    
    Yields text chunks as they arrive.
    """
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