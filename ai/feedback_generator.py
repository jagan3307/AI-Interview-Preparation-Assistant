"""
Feedback Generator - Generate comprehensive interview feedback reports
"""

from ai.groq_client import chat_completion
import json
import re
import logging

logger = logging.getLogger(__name__)


def generate_session_feedback(session_data: dict) -> dict:
    """Generate comprehensive feedback for a completed interview session."""
    
    questions = session_data.get("questions", [])
    answers = session_data.get("answers", [])
    evaluations = session_data.get("evaluations", [])
    interview_type = session_data.get("type", "technical")
    score = session_data.get("score", 0)
    
    qa_summary = ""
    for i, (q, a, e) in enumerate(zip(questions[:5], answers[:5], evaluations[:5])):
        qa_summary += f"Q{i+1}: {q.get('question', '')[:100]}\n"
        qa_summary += f"Score: {e.get('score', 'N/A')}/10\n"
        qa_summary += f"Key issue: {e.get('improvements', [''])[0] if e.get('improvements') else 'None'}\n\n"
    
    prompt = f"""
Generate a comprehensive interview feedback report.

Interview Type: {interview_type}
Overall Score: {score}%
Number of Questions: {len(questions)}

Q&A Summary:
{qa_summary}

Return JSON:
{{
  "executive_summary": "2-3 sentence overview of performance",
  "overall_performance": {{
    "score": {score},
    "grade": "Excellent/Good/Average/Poor",
    "percentile_estimate": "top X% of candidates"
  }},
  "key_strengths": ["strength1", "strength2", "strength3"],
  "critical_improvements": ["improvement1", "improvement2"],
  "skill_assessment": {{
    "technical_knowledge": <0-100>,
    "communication": <0-100>,
    "problem_solving": <0-100>,
    "confidence": <0-100>
  }},
  "action_plan": [
    {{"week": "Week 1-2", "focus": "topic", "activities": ["activity1"]}}
  ],
  "encouragement": "motivational closing message",
  "next_steps": ["step1", "step2", "step3"]
}}

Return ONLY valid JSON.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1500,
        )
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"```(?:json)?", "", cleaned).strip().rstrip("```").strip()
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Feedback generation error: {e}")
        return {
            "executive_summary": "Session completed. Detailed feedback unavailable.",
            "overall_performance": {"score": score, "grade": "Average"},
            "key_strengths": [],
            "critical_improvements": [],
        }