"""
ATS Score Calculator - Calculate Applicant Tracking System compatibility score
"""

import re
from config import ATS_KEYWORDS_WEIGHT, ATS_FORMAT_WEIGHT, ATS_CONTENT_WEIGHT

# Common ATS-friendly keywords by category
COMMON_TECH_KEYWORDS = [
    "python", "java", "javascript", "sql", "html", "css", "react", "node",
    "machine learning", "deep learning", "data science", "aws", "docker",
    "kubernetes", "git", "agile", "scrum", "rest api", "microservices",
    "tensorflow", "pytorch", "pandas", "numpy", "django", "flask",
]

COMMON_SOFT_KEYWORDS = [
    "leadership", "communication", "teamwork", "problem solving", "analytical",
    "collaborative", "detail-oriented", "proactive", "innovative", "strategic",
    "mentor", "stakeholder", "presentation", "cross-functional",
]

ACTION_VERBS = [
    "developed", "implemented", "designed", "built", "created", "managed",
    "led", "optimized", "improved", "analyzed", "delivered", "launched",
    "collaborated", "architected", "deployed", "automated", "increased",
    "reduced", "achieved", "coordinated",
]


def calculate_ats_score(resume_text: str, extracted_info: dict = None) -> dict:
    """
    Calculate comprehensive ATS score.
    
    Returns score breakdown and recommendations.
    """
    text_lower = resume_text.lower()
    
    # 1. Keywords Score
    keyword_score = _calculate_keyword_score(text_lower)
    
    # 2. Format Score
    format_score = _calculate_format_score(resume_text, extracted_info or {})
    
    # 3. Content Quality Score
    content_score = _calculate_content_score(resume_text, extracted_info or {})
    
    # Weighted average
    overall = (
        keyword_score * ATS_KEYWORDS_WEIGHT
        + format_score * ATS_FORMAT_WEIGHT
        + content_score * ATS_CONTENT_WEIGHT
    )
    
    return {
        "overall": round(overall),
        "keywords": round(keyword_score),
        "format": round(format_score),
        "content": round(content_score),
        "matched_keywords": _get_matched_keywords(text_lower),
        "missing_keywords": _get_missing_keywords(text_lower),
        "recommendations": _get_recommendations(keyword_score, format_score, content_score),
    }


def _calculate_keyword_score(text_lower: str) -> float:
    """Score based on relevant keyword presence."""
    tech_matches = sum(1 for kw in COMMON_TECH_KEYWORDS if kw in text_lower)
    soft_matches = sum(1 for kw in COMMON_SOFT_KEYWORDS if kw in text_lower)
    verb_matches = sum(1 for v in ACTION_VERBS if v in text_lower)
    
    tech_score = min(tech_matches / 10 * 100, 100)
    soft_score = min(soft_matches / 5 * 100, 100)
    verb_score = min(verb_matches / 8 * 100, 100)
    
    return (tech_score * 0.5 + soft_score * 0.25 + verb_score * 0.25)


def _calculate_format_score(text: str, info: dict) -> float:
    """Score based on resume format and completeness."""
    score = 0
    max_score = 100
    
    checks = {
        "has_email": bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)),
        "has_phone": bool(re.search(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)),
        "has_name": bool(info.get("name")),
        "has_education": bool(info.get("education")),
        "has_experience": bool(info.get("experience")),
        "has_skills": bool(info.get("skills")),
        "has_projects": bool(info.get("projects")),
        "good_length": 300 <= len(text.split()) <= 800,
        "has_linkedin": bool(info.get("linkedin") or "linkedin" in text.lower()),
        "no_special_chars": not bool(re.search(r'[<>{}|]', text)),
    }
    
    score = sum(10 for check in checks.values() if check)
    return score


def _calculate_content_score(text: str, info: dict) -> float:
    """Score based on content quality."""
    score = 0
    
    # Check for quantifiable achievements
    numbers = re.findall(r'\b\d+[%+]?\b', text)
    if len(numbers) >= 5:
        score += 20
    elif len(numbers) >= 2:
        score += 10
    
    # Check for action verbs
    verb_count = sum(1 for v in ACTION_VERBS if v in text.lower())
    score += min(verb_count * 5, 30)
    
    # Check for certifications
    if info.get("certifications"):
        score += 15
    
    # Check for multiple skills
    all_skills = []
    for cat, skills in info.get("skills", {}).items():
        if isinstance(skills, list):
            all_skills.extend(skills)
    if len(all_skills) >= 10:
        score += 20
    elif len(all_skills) >= 5:
        score += 10
    
    # Check summary
    if info.get("summary") and len(info["summary"]) > 50:
        score += 15
    
    return min(score, 100)


def _get_matched_keywords(text_lower: str) -> list:
    return [kw for kw in COMMON_TECH_KEYWORDS[:15] if kw in text_lower]


def _get_missing_keywords(text_lower: str) -> list:
    missing = [kw for kw in COMMON_TECH_KEYWORDS if kw not in text_lower]
    return missing[:10]


def _get_recommendations(kw_score: float, fmt_score: float, cnt_score: float) -> list:
    recs = []
    if kw_score < 60:
        recs.append("Add more industry-relevant keywords and technical skills")
    if fmt_score < 70:
        recs.append("Ensure contact info, education, experience, and skills sections are present")
    if cnt_score < 60:
        recs.append("Include quantifiable achievements (percentages, numbers, metrics)")
    if kw_score >= 80:
        recs.append("Strong keyword presence - good ATS compatibility")
    return recs if recs else ["Resume is well-optimized for ATS systems"]