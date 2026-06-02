"""
Application Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

APP_CONFIG = {
    "app_name": "AI Interview Assistant",
    "app_icon": "🎯",
    "version": "1.0.0",
    "description": "AI-powered interview preparation platform",
}

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "2048"))
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.7"))

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# App Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# Interview Settings
MAX_INTERVIEW_QUESTIONS = 10
MAX_FOLLOW_UP_QUESTIONS = 3
DEFAULT_INTERVIEW_DURATION = 30  # minutes

# File Upload Settings
MAX_FILE_SIZE_MB = 10
ALLOWED_RESUME_TYPES = ["pdf", "docx", "doc"]

# ATS Settings
ATS_KEYWORDS_WEIGHT = 0.4
ATS_FORMAT_WEIGHT = 0.3
ATS_CONTENT_WEIGHT = 0.3

# Companies for preparation
SUPPORTED_COMPANIES = [
    "Google", "Microsoft", "Amazon", "Meta", "Apple",
    "TCS", "Infosys", "Wipro", "Accenture", "Cognizant",
    "HCL", "Tech Mahindra", "Capgemini", "IBM", "Oracle",
]

# Interview domains
TECHNICAL_DOMAINS = {
    "Programming": ["Python", "Java", "C++", "JavaScript", "Go", "Rust"],
    "Computer Science": ["Data Structures", "Algorithms", "DBMS", "OS", "Computer Networks", "OOP"],
    "Web Development": ["HTML/CSS", "React", "Node.js", "Django", "Flask", "FastAPI"],
    "Cloud & DevOps": ["AWS", "GCP", "Azure", "Docker", "Kubernetes", "CI/CD"],
    "AI & ML": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Data Science"],
    "Database": ["SQL", "NoSQL", "MongoDB", "PostgreSQL", "Redis"],
}

NON_TECHNICAL_ROLES = [
    "HR", "Marketing", "Sales", "Business Analyst",
    "Operations", "Customer Support", "Project Management",
    "Finance", "Supply Chain", "Product Management",
]

DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

# Aptitude categories
APTITUDE_CATEGORIES = {
    "Quantitative": ["Percentages", "Profit & Loss", "Time & Work", "Probability", "Ratios"],
    "Logical": ["Puzzles", "Blood Relations", "Seating Arrangement", "Coding-Decoding"],
    "Verbal": ["Grammar", "Vocabulary", "Reading Comprehension", "Synonyms/Antonyms"],
}