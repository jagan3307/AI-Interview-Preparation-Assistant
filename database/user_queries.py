"""
User Database Queries
"""

from database.supabase_client import get_db, execute_query
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_user_profile(user_id: str, email: str, full_name: str = "", **kwargs) -> dict:
    """Create a new user profile."""
    try:
        db = get_db()
        data = {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_admin": False,
            "profile_completed": False,
            **kwargs,
        }
        result = db.table("user_profiles").upsert(data).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        logger.error(f"Error creating user profile: {e}")
        return {}


def get_user_profile(user_id: str) -> dict:
    """Get user profile by ID."""
    try:
        db = get_db()
        result = db.table("user_profiles").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        return {}


def update_user_profile(user_id: str, updates: dict) -> dict:
    """Update user profile."""
    try:
        db = get_db()
        updates["updated_at"] = datetime.utcnow().isoformat()
        result = db.table("user_profiles").update(updates).eq("id", user_id).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        return {}


def get_user_stats(user_id: str) -> dict:
    """Get aggregated user statistics."""
    try:
        db = get_db()
        interviews = db.table("interview_sessions").select("*").eq("user_id", user_id).execute()
        resumes = db.table("resume_analyses").select("*").eq("user_id", user_id).execute()
        
        sessions = interviews.data or []
        total_interviews = len(sessions)
        avg_score = sum(s.get("score", 0) for s in sessions) / max(total_interviews, 1)
        
        return {
            "total_interviews": total_interviews,
            "average_score": round(avg_score, 1),
            "resumes_uploaded": len(resumes.data or []),
            "last_activity": sessions[-1]["created_at"] if sessions else None,
        }
    except Exception as e:
        logger.error(f"Error fetching user stats: {e}")
        return {"total_interviews": 0, "average_score": 0, "resumes_uploaded": 0}


def get_all_users(limit: int = 100) -> list:
    """Get all users (admin only)."""
    try:
        db = get_db()
        result = db.table("user_profiles").select("*").limit(limit).order("created_at", desc=True).execute()
        return result.data or []
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return []