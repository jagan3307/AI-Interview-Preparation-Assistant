"""
AI Answer Evaluator - Evaluate and score interview answers
"""

from ai.groq_client import chat_completion
import json
import re
import logging

logger = logging.getLogger(__name__)


def evaluate_answer(
    question: str,
    answer: str,
    interview_type: str = "technical",
    expected_topics: list = None,
) -> dict:
    """
    Evaluate a candidate's answer to an interview question.
    
    Returns score, feedback, strengths, improvements.
    """
    topics_text = f"\nExpected topics to cover: {', '.join(expected_topics)}" if expected_topics else ""
    
    prompt = f"""
You are an expert {interview_type} interviewer. Evaluate this answer:

Question: {question}
Candidate's Answer: {answer}{topics_text}

Return JSON:
{{
  "score": <0-10>,
  "grade": "Excellent/Good/Average/Poor",
  "strengths": ["what was good"],
  "improvements": ["what could be better"],
  "missed_points": ["important points not covered"],
  "technical_accuracy": <0-10>,
  "communication_clarity": <0-10>,
  "depth": <0-10>,
  "detailed_feedback": "2-3 sentence constructive feedback",
  "model_answer_hints": ["key points of a great answer"]
}}

Be constructive, specific, and encouraging. Return ONLY valid JSON.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
        )
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"```(?:json)?", "", cleaned).strip().rstrip("```").strip()
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Answer evaluation error: {e}")
        return _default_evaluation()


def evaluate_hr_answer(question: str, answer: str) -> dict:
    """Evaluate HR/behavioral interview answer with STAR analysis."""
    
    prompt = f"""
Evaluate this HR interview answer using the STAR method:

Question: {question}
Answer: {answer}

Return JSON:
{{
  "score": <0-10>,
  "star_analysis": {{
    "situation": {{"present": true/false, "quality": "Good/Partial/Missing", "comment": ""}},
    "task": {{"present": true/false, "quality": "Good/Partial/Missing", "comment": ""}},
    "action": {{"present": true/false, "quality": "Good/Partial/Missing", "comment": ""}},
    "result": {{"present": true/false, "quality": "Good/Partial/Missing", "comment": ""}}
  }},
  "competencies": {{
    "communication": <0-10>,
    "leadership": <0-10>,
    "teamwork": <0-10>,
    "problem_solving": <0-10>,
    "professionalism": <0-10>
  }},
  "confidence_indicators": ["indicators from the answer"],
  "red_flags": [],
  "positive_signals": [],
  "feedback": "constructive feedback",
  "improvement_tips": ["specific tips"]
}}

Return ONLY valid JSON.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1200,
        )
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"```(?:json)?", "", cleaned).strip().rstrip("```").strip()
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"HR evaluation error: {e}")
        return _default_evaluation()


def evaluate_code(code: str, question: dict) -> dict:
    """Evaluate submitted code solution."""
    
    prompt = f"""
Evaluate this code solution:

Problem: {question.get('title', '')}
Description: {question.get('description', '')[:500]}

Submitted Code:
```
{code[:2000]}
```

Return JSON:
{{
  "correctness": <0-10>,
  "code_quality": <0-10>,
  "time_complexity": {{
    "actual": "O(n)",
    "optimal": "O(n log n)",
    "score": <0-10>
  }},
  "space_complexity": {{
    "actual": "O(n)",
    "optimal": "O(1)",
    "score": <0-10>
  }},
  "overall_score": <0-10>,
  "passes_test_cases": true/false,
  "issues": ["issue1", "issue2"],
  "improvements": ["improvement1"],
  "good_practices": ["good thing1"],
  "feedback": "detailed feedback"
}}

Return ONLY valid JSON.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000,
        )
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"```(?:json)?", "", cleaned).strip().rstrip("```").strip()
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Code evaluation error: {e}")
        return {"overall_score": 5, "feedback": "Evaluation failed. Please try again."}


def calculate_session_score(evaluations: list) -> dict:
    """Calculate overall session score from individual evaluations."""
    if not evaluations:
        return {"overall": 0, "grade": "N/A"}
    
    scores = [e.get("score", 0) for e in evaluations if isinstance(e.get("score"), (int, float))]
    if not scores:
        return {"overall": 0, "grade": "N/A"}
    
    avg = sum(scores) / len(scores)
    
    if avg >= 8:
        grade = "Excellent"
    elif avg >= 6:
        grade = "Good"
    elif avg >= 4:
        grade = "Average"
    else:
        grade = "Needs Improvement"
    
    return {
        "overall": round(avg * 10),  # Convert to percentage
        "raw_score": round(avg, 1),
        "grade": grade,
        "total_questions": len(evaluations),
        "scores": scores,
    }


def _default_evaluation() -> dict:
    return {
        "score": 5,
        "grade": "Average",
        "strengths": ["Answer provided"],
        "improvements": ["Could not evaluate - please try again"],
        "missed_points": [],
        "technical_accuracy": 5,
        "communication_clarity": 5,
        "depth": 5,
        "detailed_feedback": "Evaluation could not be completed. Please try again.",
        "model_answer_hints": [],
    }