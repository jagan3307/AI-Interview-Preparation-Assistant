"""
AI Resume Analyzer - Extract information and analyze resumes
"""

from ai.groq_client import chat_completion
from utils.prompts import RESUME_ANALYSIS_PROMPT, RESUME_EXTRACTION_PROMPT
import json
import logging
import re

logger = logging.getLogger(__name__)


def extract_resume_info(resume_text: str) -> dict:
    """
    Extract structured information from resume text using AI.
    
    Returns dict with name, contact, education, skills, experience, etc.
    """
    prompt = f"""
Extract all information from this resume and return as JSON with these exact keys:
{{
  "name": "Full name",
  "email": "email address",
  "phone": "phone number",
  "location": "city/location",
  "linkedin": "linkedin url if present",
  "github": "github url if present",
  "summary": "professional summary/objective",
  "education": [
    {{"degree": "", "institution": "", "year": "", "gpa": ""}}
  ],
  "experience": [
    {{"title": "", "company": "", "duration": "", "responsibilities": []}}
  ],
  "skills": {{
    "technical": [],
    "soft": [],
    "languages": [],
    "frameworks": [],
    "tools": [],
    "databases": [],
    "cloud": []
  }},
  "projects": [
    {{"name": "", "description": "", "technologies": [], "url": ""}}
  ],
  "certifications": [
    {{"name": "", "issuer": "", "year": ""}}
  ],
  "achievements": []
}}

Resume Text:
{resume_text[:4000]}

Return ONLY valid JSON, no markdown, no explanation.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000,
        )
        
        # Clean response
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"```(?:json)?", "", cleaned).strip().rstrip("```").strip()
        
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in resume extraction: {e}")
        return _fallback_extraction(resume_text)
    except Exception as e:
        logger.error(f"Resume extraction error: {e}")
        return {}


def analyze_resume(resume_text: str, extracted_info: dict) -> dict:
    """
    Perform comprehensive resume analysis.
    
    Returns ATS score, strengths, weaknesses, suggestions, etc.
    """
    skills_list = []
    if extracted_info.get("skills"):
        for category, skills in extracted_info["skills"].items():
            if isinstance(skills, list):
                skills_list.extend(skills)
    
    prompt = f"""
Analyze this resume and provide a comprehensive evaluation. Return JSON with these exact keys:

{{
  "ats_score": <number 0-100>,
  "ats_breakdown": {{
    "keywords": <0-100>,
    "formatting": <0-100>,
    "content_quality": <0-100>,
    "completeness": <0-100>
  }},
  "strengths": ["strength1", "strength2", ...],
  "weaknesses": ["weakness1", "weakness2", ...],
  "missing_keywords": ["keyword1", "keyword2", ...],
  "improvement_suggestions": [
    {{"area": "area_name", "suggestion": "detailed suggestion", "priority": "high/medium/low"}}
  ],
  "recommended_certifications": ["cert1", "cert2", ...],
  "recommended_projects": ["project_idea1", "project_idea2", ...],
  "overall_assessment": "2-3 sentence overall assessment",
  "interview_readiness": <0-100>
}}

Resume Summary:
- Skills: {', '.join(skills_list[:20])}
- Education: {json.dumps(extracted_info.get('education', [])[:2])}
- Experience count: {len(extracted_info.get('experience', []))}
- Projects count: {len(extracted_info.get('projects', []))}
- Certifications: {len(extracted_info.get('certifications', []))}

Resume Text (first 2000 chars):
{resume_text[:2000]}

Return ONLY valid JSON.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2000,
        )
        
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"```(?:json)?", "", cleaned).strip().rstrip("```").strip()
        
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Resume analysis error: {e}")
        return _default_analysis()


def _fallback_extraction(resume_text: str) -> dict:
    """Basic fallback extraction using regex."""
    import re
    
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
    phone_match = re.search(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', resume_text)
    
    return {
        "name": "",
        "email": email_match.group() if email_match else "",
        "phone": phone_match.group() if phone_match else "",
        "skills": {"technical": [], "soft": []},
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "achievements": [],
    }


def _default_analysis() -> dict:
    """Default analysis when AI fails."""
    return {
        "ats_score": 50,
        "ats_breakdown": {"keywords": 50, "formatting": 50, "content_quality": 50, "completeness": 50},
        "strengths": ["Resume submitted successfully"],
        "weaknesses": ["Analysis incomplete - please try again"],
        "missing_keywords": [],
        "improvement_suggestions": [],
        "recommended_certifications": [],
        "recommended_projects": [],
        "overall_assessment": "Analysis could not be completed. Please try again.",
        "interview_readiness": 50,
    }