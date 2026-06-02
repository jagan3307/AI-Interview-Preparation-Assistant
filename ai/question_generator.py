"""
AI Question Generator - Generate interview questions from various sources
"""

from ai.groq_client import chat_completion
import json
import re
import logging

logger = logging.getLogger(__name__)


def generate_resume_questions(extracted_info: dict, num_questions: int = 10) -> list:
    """
    Generate personalized interview questions based on resume content.
    
    Returns list of question dicts with category and difficulty.
    """
    skills = []
    for cat, items in extracted_info.get("skills", {}).items():
        if isinstance(items, list):
            skills.extend(items[:5])
    
    projects = [p.get("name", "") + ": " + p.get("description", "")[:100]
                for p in extracted_info.get("projects", [])[:3]]
    
    experience = [e.get("title", "") + " at " + e.get("company", "")
                  for e in extracted_info.get("experience", [])[:3]]
    
    certifications = [c.get("name", "") for c in extracted_info.get("certifications", [])[:3]]
    
    prompt = f"""
Generate {num_questions} personalized interview questions based on this candidate's resume.
Return a JSON array with each question having these fields:
[
  {{
    "id": 1,
    "question": "question text",
    "category": "skills/projects/experience/certifications/behavioral",
    "difficulty": "Easy/Medium/Hard",
    "expected_topics": ["topic1", "topic2"],
    "follow_up_hint": "what to probe deeper on"
  }}
]

Candidate Profile:
- Skills: {', '.join(skills[:15])}
- Projects: {'; '.join(projects)}
- Experience: {'; '.join(experience)}
- Certifications: {', '.join(certifications)}

Mix of question types: technical depth, project architecture, problem-solving, behavioral.
Return ONLY valid JSON array.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )
        return _parse_json_array(response)
    except Exception as e:
        logger.error(f"Resume question generation error: {e}")
        return []


def generate_technical_questions(
    domain: str,
    topic: str,
    difficulty: str = "Medium",
    num_questions: int = 10,
) -> list:
    """Generate technical interview questions for a specific domain/topic."""
    
    prompt = f"""
Generate {num_questions} {difficulty} difficulty technical interview questions for:
Domain: {domain}
Topic: {topic}

Return JSON array:
[
  {{
    "id": 1,
    "question": "question text",
    "type": "conceptual/practical/problem-solving/design",
    "difficulty": "{difficulty}",
    "key_points": ["point1", "point2"],
    "sample_answer_outline": "brief outline of expected answer",
    "follow_up": "potential follow-up question"
  }}
]

Make questions progressively deeper. Include conceptual, practical, and design questions.
Return ONLY valid JSON array.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )
        return _parse_json_array(response)
    except Exception as e:
        logger.error(f"Technical question generation error: {e}")
        return []


def generate_hr_questions(context: str = "", num_questions: int = 10) -> list:
    """Generate HR and behavioral interview questions."""
    
    prompt = f"""
Generate {num_questions} HR/behavioral interview questions.
{f'Context: {context}' if context else ''}

Include STAR-method questions, behavioral, situational, and motivational questions.

Return JSON array:
[
  {{
    "id": 1,
    "question": "question text",
    "type": "behavioral/situational/motivational/background",
    "evaluation_criteria": ["criterion1", "criterion2"],
    "star_applicable": true/false,
    "red_flags": ["what to watch out for"]
  }}
]

Return ONLY valid JSON array.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )
        return _parse_json_array(response)
    except Exception as e:
        logger.error(f"HR question generation error: {e}")
        return []


def generate_aptitude_questions(category: str, subcategory: str, num_questions: int = 10) -> list:
    """Generate aptitude test questions."""
    
    prompt = f"""
Generate {num_questions} aptitude questions for:
Category: {category}
Sub-category: {subcategory}

Return JSON array:
[
  {{
    "id": 1,
    "question": "question text",
    "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
    "correct_answer": "A",
    "explanation": "why this is correct",
    "difficulty": "Easy/Medium/Hard",
    "time_limit_seconds": 60
  }}
]

Include clear numerical/logical problems with one correct answer.
Return ONLY valid JSON array.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
        )
        return _parse_json_array(response)
    except Exception as e:
        logger.error(f"Aptitude question generation error: {e}")
        return []


def generate_coding_question(difficulty: str = "Medium", topic: str = "Arrays") -> dict:
    """Generate a single coding interview question."""
    
    prompt = f"""
Generate a {difficulty} coding interview question about {topic}.

Return JSON object:
{{
  "title": "Problem title",
  "description": "Full problem description",
  "examples": [
    {{"input": "example input", "output": "expected output", "explanation": "why"}}
  ],
  "constraints": ["constraint1", "constraint2"],
  "hints": ["hint1", "hint2"],
  "difficulty": "{difficulty}",
  "topic": "{topic}",
  "time_complexity": "expected O(n) solution",
  "space_complexity": "expected O(n) space",
  "sample_solution": "pseudocode or approach description",
  "test_cases": [
    {{"input": "test1", "expected": "output1"}},
    {{"input": "test2", "expected": "output2"}}
  ]
}}

Return ONLY valid JSON.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2000,
        )
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"```(?:json)?", "", cleaned).strip().rstrip("```").strip()
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Coding question generation error: {e}")
        return {}


def generate_company_questions(company: str, role: str = "Software Engineer", num_questions: int = 10) -> dict:
    """Generate company-specific interview questions and patterns."""
    
    prompt = f"""
Generate interview preparation material for {company} - {role} position.

Return JSON:
{{
  "company_overview": "brief interview culture description",
  "interview_process": ["round1", "round2", "round3"],
  "key_focus_areas": ["area1", "area2"],
  "questions": [
    {{
      "question": "question text",
      "category": "technical/behavioral/system-design",
      "difficulty": "Easy/Medium/Hard",
      "why_asked": "reason this company asks this"
    }}
  ],
  "preparation_tips": ["tip1", "tip2"],
  "common_mistakes": ["mistake1", "mistake2"],
  "resources": ["resource1", "resource2"]
}}

Return ONLY valid JSON.
"""
    
    try:
        response = chat_completion(
            [{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=2000,
        )
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"```(?:json)?", "", cleaned).strip().rstrip("```").strip()
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Company question generation error: {e}")
        return {}


def _parse_json_array(response: str) -> list:
    """Parse JSON array from AI response."""
    try:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"```(?:json)?", "", cleaned).strip().rstrip("```").strip()
        
        # Find JSON array in response
        start = cleaned.find("[")
        end = cleaned.rfind("]") + 1
        if start != -1 and end > start:
            cleaned = cleaned[start:end]
        
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"JSON parse error: {e}\nResponse: {response[:200]}")
        return []