"""
Interview Session Database Queries
"""

from database.supabase_client import get_db
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


def save_interview_session(user_id: str, session_data: dict) -> str:
    """Save a complete interview session and return session ID."""
    try:
        db = get_db()
        data = {
            "user_id": user_id,
            "interview_type": session_data.get("type", "technical"),
            "domain": session_data.get("domain", ""),
            "difficulty": session_data.get("difficulty", "Medium"),
            "questions": json.dumps(session_data.get("questions", [])),
            "answers": json.dumps(session_data.get("answers", [])),
            "evaluations": json.dumps(session_data.get("evaluations", [])),
            "score": session_data.get("score", 0),
            "feedback": session_data.get("feedback", ""),
            "duration_minutes": session_data.get("duration", 0),
            "company": session_data.get("company", ""),
            "created_at": datetime.utcnow().isoformat(),
        }
        result = db.table("interview_sessions").insert(data).execute()
        return result.data[0]["id"] if result.data else ""
    except Exception as e:
        logger.error(f"Error saving interview session: {e}")
        return ""


def get_interview_sessions(user_id: str, interview_type: str = None, limit: int = 50) -> list:
    """Get user's interview sessions."""
    try:
        db = get_db()
        query = db.table("interview_sessions").select("*").eq("user_id", user_id)
        if interview_type:
            query = query.eq("interview_type", interview_type)
        result = query.order("created_at", desc=True).limit(limit).execute()
        sessions = result.data or []
        # Parse JSON fields
        for s in sessions:
            for field in ["questions", "answers", "evaluations"]:
                if s.get(field) and isinstance(s[field], str):
                    try:
                        s[field] = json.loads(s[field])
                    except Exception:
                        s[field] = []
        return sessions
    except Exception as e:
        logger.error(f"Error fetching interview sessions: {e}")
        return []


def get_interview_session(session_id: str) -> dict:
    """Get a specific interview session."""
    try:
        db = get_db()
        result = db.table("interview_sessions").select("*").eq("id", session_id).execute()
        if result.data:
            s = result.data[0]
            for field in ["questions", "answers", "evaluations"]:
                if s.get(field) and isinstance(s[field], str):
                    try:
                        s[field] = json.loads(s[field])
                    except Exception:
                        s[field] = []
            return s
        return {}
    except Exception as e:
        logger.error(f"Error fetching session: {e}")
        return {}


def get_performance_trends(user_id: str) -> list:
    """Get score trends over time."""
    try:
        db = get_db()
        result = (
            db.table("interview_sessions")
            .select("created_at,score,interview_type,domain")
            .eq("user_id", user_id)
            .order("created_at")
            .execute()
        )
        return result.data or []
    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        return []


def save_aptitude_result(user_id: str, result_data: dict) -> bool:
    """Save aptitude test result."""
    try:
        db = get_db()
        data = {
            "user_id": user_id,
            "category": result_data.get("category", ""),
            "score": result_data.get("score", 0),
            "total_questions": result_data.get("total", 0),
            "correct_answers": result_data.get("correct", 0),
            "time_taken": result_data.get("time_taken", 0),
            "created_at": datetime.utcnow().isoformat(),
        }
        db.table("aptitude_results").insert(data).execute()
        return True
    except Exception as e:
        logger.error(f"Error saving aptitude result: {e}")
        return False