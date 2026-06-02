"""
Career Guidance System - AI-powered career recommendations
"""

from ai.groq_client import chat_completion
import json
import re
import logging

logger = logging.getLogger(__name__)


def generate_career_guidance(
    resume_info: dict,
    interview_scores: dict = None,
    skill_scores: dict = None,
    aptitude_scores: dict = None,
) -> dict:
    """
    Generate comprehensive career guidance based on all available data.
    
    Returns career paths, roadmaps, certifications, courses.
    """
    skills = []
    for cat, items in resume_info.get("skills", {}).items():
        if isinstance(items, list):
            skills.extend(items)
    
    experience_years = len(resume_info.get("experience", []))
    education = resume_info.get("education", [{}])
    degree = education[0].get("degree", "") if education else ""
    
    performance_summary = ""
    if interview_scores:
        performance_summary += f"Interview Performance: {interview_scores.get('overall', 'N/A')}%\n"
    if skill_scores:
        top_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        performance_summary += f"Top Skills: {', '.join([f'{s}({v}%)' for s, v in top_skills])}\n"
    
    prompt = f"""
Generate comprehensive career guidance for this candidate.

Profile:
- Current Skills: {', '.join(skills[:15])}
- Experience Level: {experience_years} positions
- Education: {degree}
- Performance: {performance_summary or 'No data yet'}

Return JSON:
{{
  "career_paths": [
    {{
      "title": "Career Path Name",
      "description": "2-3 sentence description",
      "match_percentage": <0-100>,
      "required_skills": ["skill1", "skill2"],
      "missing_skills": ["skill1", "skill2"],
      "salary_range": "min-max USD",
      "growth_outlook": "High/Medium/Low",
      "timeline": "time to reach"
    }}
  ],
  "immediate_actions": ["action1", "action2"],
  "learning_roadmap": [
    {{
      "phase": "Phase 1 - Foundation",
      "duration": "1-2 months",
      "goals": ["goal1", "goal2"],
      "resources": ["resource1"]
    }}
  ],
  "recommended_certifications": [
    {{
      "name": "cert name",
      "provider": "AWS/Google/etc",
      "relevance": "why relevant",
      "difficulty": "Beginner/Intermediate/Advanced",
      "estimated_time": "weeks"
    }}
  ],
  "recommended_courses": [
    {{
      "title": "course title",
      "platform": "Coursera/Udemy/etc",
      "topic": "what it covers",
      "priority": "High/Medium/Low"
    }}
  ],
  "industry_trends": ["trend1", "trend2"],
  "strengths_to_leverage": ["strength1", "strength2"],
  "gaps_to_address": ["gap1", "gap2"],
  "overall_advice": "2-3 sentences of personalized advice"
}}

Provide 3 career paths, 3 learning phases, 5 certifications, 5 courses.
Return ONLY valid JSON.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=2500,
        )
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"```(?:json)?", "", cleaned).strip().rstrip("```").strip()
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Career guidance error: {e}")
        return {"career_paths": [], "overall_advice": "Unable to generate guidance. Please try again."}


def get_learning_resources(skill: str, level: str = "intermediate") -> list:
    """Get learning resources for a specific skill."""
    prompt = f"""
List 5 best learning resources for {skill} at {level} level.

Return JSON array:
[
  {{
    "title": "resource name",
    "type": "course/book/tutorial/video",
    "platform": "platform name",
    "url_hint": "search term to find it",
    "free": true/false,
    "duration": "estimated time",
    "description": "what you'll learn"
  }}
]

Return ONLY valid JSON array.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1000,
        )
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"```(?:json)?", "", cleaned).strip().rstrip("```").strip()
        start = cleaned.find("[")
        end = cleaned.rfind("]") + 1
        if start != -1:
            cleaned = cleaned[start:end]
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Resources error: {e}")
        return []