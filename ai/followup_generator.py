"""
AI Follow-Up Question Engine - Generate intelligent follow-up questions
"""

from ai.groq_client import chat_completion
import logging

logger = logging.getLogger(__name__)


def generate_followup(
    question: str,
    answer: str,
    conversation_history: list = None,
    interview_type: str = "technical",
) -> str:
    """
    Generate an intelligent follow-up question based on candidate's answer.
    
    Args:
        question: The original question asked
        answer: Candidate's answer
        conversation_history: Previous Q&A pairs
        interview_type: Type of interview (technical, hr, etc.)
    
    Returns:
        Follow-up question string
    """
    history_text = ""
    if conversation_history:
        for item in conversation_history[-3:]:  # Last 3 exchanges
            history_text += f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}\n\n"
    
    prompt = f"""You are an expert {interview_type} interviewer. Based on the candidate's answer, generate ONE intelligent follow-up question.

{f'Previous conversation:{history_text}' if history_text else ''}

Original Question: {question}
Candidate's Answer: {answer}

Generate a follow-up that:
1. Probes deeper into their answer
2. Tests understanding of concepts they mentioned
3. Uncovers any gaps or assumptions
4. Is natural and conversational

Return ONLY the follow-up question, nothing else. No prefixes like "Follow-up:" just the question itself.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200,
        )
        return response.strip()
    except Exception as e:
        logger.error(f"Follow-up generation error: {e}")
        return "Can you elaborate more on that point?"


def should_ask_followup(answer: str) -> bool:
    """Determine if a follow-up question is warranted based on answer quality."""
    
    # Short answers likely need follow-up
    if len(answer.split()) < 20:
        return True
    
    # Vague answers need follow-up
    vague_phrases = [
        "i think", "maybe", "i'm not sure", "i don't know",
        "something like", "basically", "kind of", "sort of",
    ]
    
    answer_lower = answer.lower()
    vague_count = sum(1 for phrase in vague_phrases if phrase in answer_lower)
    
    return vague_count >= 2


def generate_clarification(question: str, unclear_part: str) -> str:
    """Generate a clarification question."""
    prompt = f"""As an interviewer, the candidate's answer was unclear regarding: "{unclear_part}"

Original question: {question}

Generate a polite clarification question. Return ONLY the question.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=150,
        )
        return response.strip()
    except Exception as e:
        logger.error(f"Clarification generation error: {e}")
        return f"Could you clarify what you mean by that?"