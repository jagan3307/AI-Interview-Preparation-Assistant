"""
Centralized AI Prompts
"""

# ---------------------------------
# Resume Analysis
# ---------------------------------

RESUME_ANALYSIS_PROMPT = """
Analyze the uploaded resume.

Extract:

1. Personal Information
2. Skills
3. Projects
4. Experience
5. Education
6. Certifications

Provide:

- ATS Score
- Strengths
- Weaknesses
- Missing Keywords
- Improvement Suggestions

Return JSON only.
"""

# ---------------------------------
# Technical Interview
# ---------------------------------

TECHNICAL_QUESTION_PROMPT = """
Generate technical interview questions.

Requirements:

- Conceptual
- Practical
- Scenario Based
- Increasing Difficulty

Return JSON only.
"""

# ---------------------------------
# HR Interview
# ---------------------------------

HR_QUESTION_PROMPT = """
Generate HR interview questions.

Include:

- Tell me about yourself
- Leadership
- Teamwork
- Conflict Resolution
- Career Goals

Return JSON only.
"""

# ---------------------------------
# Coding Interview
# ---------------------------------

CODING_QUESTION_PROMPT = """
Generate coding interview problem.

Include:

- Problem Statement
- Constraints
- Examples
- Test Cases
- Complexity

Return JSON only.
"""

# ---------------------------------
# Answer Evaluation
# ---------------------------------

ANSWER_EVALUATION_PROMPT = """
Evaluate interview answer.

Return:

- Score
- Strengths
- Weaknesses
- Missed Points
- Feedback
- Suggested Answer

Return JSON only.
"""

# ---------------------------------
# Career Guidance
# ---------------------------------

CAREER_GUIDANCE_PROMPT = """
Analyze candidate profile.

Provide:

- Suitable Roles
- Skill Gaps
- Learning Roadmap
- Certifications
- Salary Insights

Return JSON only.
"""

# ---------------------------------
# Company Preparation
# ---------------------------------
RESUME_EXTRACTION_PROMPT = """
You are an expert resume parser.

Extract the following information from the resume and return ONLY valid JSON.

{
  "name": "",
  "email": "",
  "phone": "",
  "skills": {
    "technical": [],
    "programming": [],
    "tools": [],
    "soft_skills": []
  },
  "education": [],
  "experience": [],
  "projects": [],
  "certifications": []
}

Return valid JSON only.
"""

COMPANY_PREP_PROMPT = """
Generate company-specific preparation plan.

Include:

- Interview Process
- Common Questions
- Focus Areas
- Preparation Tips

Return JSON only.
"""