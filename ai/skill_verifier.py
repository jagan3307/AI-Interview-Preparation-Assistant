"""
Skill Verification Engine - Verify resume skills through targeted questions
"""

from ai.groq_client import chat_completion
from ai.answer_evaluator import evaluate_answer
import json
import re
import logging

logger = logging.getLogger(__name__)


def generate_skill_verification_questions(skills: list, questions_per_skill: int = 3) -> dict:
    """
    Generate targeted questions to verify each skill.
    
    Returns dict of skill -> [questions]
    """
    all_questions = {}
    
    for skill in skills[:10]:  # Limit to 10 skills
        prompt = f"""
Generate {questions_per_skill} quick verification questions for: {skill}

Return JSON array:
[
  {{
    "question": "specific technical question",
    "type": "conceptual/practical/scenario",
    "expected_answer_keywords": ["keyword1", "keyword2"],
    "difficulty": "Medium"
  }}
]

Questions should clearly differentiate someone with real experience from someone who just listed the skill.
Return ONLY valid JSON array.
"""
        try:
            response = chat_completion(
                [{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=800,
            )
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"```(?:json)?", "", cleaned).strip().rstrip("```").strip()
            start = cleaned.find("[")
            end = cleaned.rfind("]") + 1
            if start != -1:
                cleaned = cleaned[start:end]
            questions = json.loads(cleaned)
            all_questions[skill] = questions
        except Exception as e:
            logger.error(f"Skill question generation error for {skill}: {e}")
            all_questions[skill] = []
    
    return all_questions


def calculate_skill_scores(skill_evaluations: dict) -> dict:
    """
    Calculate skill proficiency scores from evaluation results.
    
    Returns dict of skill -> score (0-100)
    """
    scores = {}
    
    for skill, evaluations in skill_evaluations.items():
        if not evaluations:
            scores[skill] = 0
            continue
        
        valid_scores = [e.get("score", 0) for e in evaluations if isinstance(e.get("score"), (int, float))]
        if valid_scores:
            avg = sum(valid_scores) / len(valid_scores)
            scores[skill] = round(avg * 10)  # Convert 0-10 to 0-100
        else:
            scores[skill] = 0
    
    return scores


def get_overall_verification_score(skill_scores: dict) -> dict:
    """Calculate overall skill verification score."""
    if not skill_scores:
        return {"overall": 0, "verified_skills": [], "unverified_skills": []}
    
    scores = list(skill_scores.values())
    overall = sum(scores) / len(scores) if scores else 0
    
    verified = [skill for skill, score in skill_scores.items() if score >= 60]
    unverified = [skill for skill, score in skill_scores.items() if score < 60]
    
    return {
        "overall": round(overall),
        "verified_skills": verified,
        "unverified_skills": unverified,
        "skill_scores": skill_scores,
        "grade": _get_grade(overall),
    }


def _get_grade(score: float) -> str:
    if score >= 80:
        return "Expert"
    elif score >= 60:
        return "Proficient"
    elif score >= 40:
        return "Beginner"
    else:
        return "Needs Practice"