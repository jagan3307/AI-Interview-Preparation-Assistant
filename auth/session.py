"""
Session Management - Handle user authentication state
"""

import streamlit as st
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def init_session():
    """Initialize session state variables."""
    defaults = {
        "user": None,
        "auth_token": None,
        "current_page": "dashboard",
        "auth_page": "login",
        "interview_session": {},
        "resume_data": {},
        "notifications": [],
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_user(user_data: dict, token: str = None):
    """Set the current authenticated user."""
    st.session_state.user = user_data
    if token:
        st.session_state.auth_token = token
    st.session_state.auth_page = "login"


def get_current_user():

    if st.session_state.get("user"):
        return st.session_state.user

    try:

        from database.supabase_client import get_supabase_client
        from database.user_queries import (
            get_user_profile,
            create_user_profile
        )

        client = get_supabase_client()

        session = client.auth.get_session()

        if session and session.session:

            auth_user = session.session.user

            profile = get_user_profile(auth_user.id)

            if not profile:

                profile = create_user_profile(
                    user_id=auth_user.id,
                    email=auth_user.email,
                    full_name=auth_user.user_metadata.get(
                        "full_name",
                        ""
                    )
                )

            user_data = {
                "id": auth_user.id,
                "email": auth_user.email,
                "full_name": profile.get(
                    "full_name",
                    auth_user.user_metadata.get(
                        "full_name",
                        ""
                    )
                ),
                "is_admin": profile.get(
                    "is_admin",
                    False
                ),
                **profile
            }

            st.session_state.user = user_data

            return user_data

    except Exception as e:
        logger.error(f"Session restore error: {e}")

    return None

def logout():
    """Log out the current user."""
    try:
        from database.supabase_client import get_supabase_client
        client = get_supabase_client()
        client.auth.sign_out()
    except Exception as e:
        logger.warning(f"Supabase signout error: {e}")
    
    # Clear session
    keys_to_clear = ["user", "auth_token", "interview_session", "resume_data"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.session_state.auth_page = "login"
    st.session_state.current_page = "dashboard"


def require_auth():
    """Decorator/check to require authentication."""
    user = get_current_user()
    if not user:
        st.error("Please log in to access this feature.")
        st.stop()
    return user


def update_session_user(updates: dict):
    """Update user data in session."""
    if st.session_state.get("user"):
        st.session_state.user.update(updates)