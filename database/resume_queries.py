"""
Resume Database Queries
"""

from database.supabase_client import get_db
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


def save_resume_analysis(user_id: str, analysis_data: dict) -> str:
    """Save resume analysis result."""
    try:
        db = get_db()
        data = {
            "user_id": user_id,
            "filename": analysis_data.get("filename", ""),
            "raw_text": analysis_data.get("raw_text", "")[:5000],  # limit size
            "extracted_info": json.dumps(analysis_data.get("extracted_info", {})),
            "ats_score": analysis_data.get("ats_score", 0),
            "strengths": json.dumps(analysis_data.get("strengths", [])),
            "weaknesses": json.dumps(analysis_data.get("weaknesses", [])),
            "suggestions": json.dumps(analysis_data.get("suggestions", [])),
            "missing_keywords": json.dumps(analysis_data.get("missing_keywords", [])),
            "recommended_certifications": json.dumps(analysis_data.get("recommended_certifications", [])),
            "created_at": datetime.utcnow().isoformat(),
        }
        result = db.table("resume_analyses").insert(data).execute()
        return result.data[0]["id"] if result.data else ""
    except Exception as e:
        logger.error(f"Error saving resume analysis: {e}")
        return ""


def get_resume_analyses(user_id: str, limit: int = 10) -> list:
    """Get user's resume analyses."""
    try:
        db = get_db()
        result = (
            db.table("resume_analyses")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        analyses = result.data or []
        for a in analyses:
            for field in ["extracted_info", "strengths", "weaknesses", "suggestions", "missing_keywords", "recommended_certifications"]:
                if a.get(field) and isinstance(a[field], str):
                    try:
                        a[field] = json.loads(a[field])
                    except Exception:
                        a[field] = {}
        return analyses
    except Exception as e:
        logger.error(f"Error fetching resume analyses: {e}")
        return []

from database.supabase_client import get_db
import logging

logger = logging.getLogger(__name__)


def get_resume_history(user_id: str) -> list:
    """Get all resume analyses for a user."""
    try:
        db = get_db()

        result = (
            db.table("resume_analysis")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return result.data or []

    except Exception as e:
        logger.error(f"Error fetching resume history: {e}")
        return []
    
def get_latest_resume(user_id: str) -> dict:
    """Get the most recent resume analysis."""
    analyses = get_resume_analyses(user_id, limit=1)
    return analyses[0] if analyses else {}