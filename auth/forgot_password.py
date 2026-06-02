"""
Forgot Password Page
"""

import streamlit as st
from database.supabase_client import get_supabase_client
import logging

logger = logging.getLogger(__name__)


def show_forgot_password_page():
    """Display the forgot password page."""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🔐 Reset Password")
        st.markdown("Enter your email address and we'll send you a password reset link.")
        
        with st.form("reset_form"):
            email = st.text_input("📧 Email", placeholder="your@email.com")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("Send Reset Link", use_container_width=True, type="primary")
            with col_b:
                back = st.form_submit_button("Back to Login", use_container_width=True)
            
            if submit:
                if not email:
                    st.error("Please enter your email address.")
                else:
                    _handle_password_reset(email)
            
            if back:
                st.session_state.auth_page = "login"
                st.rerun()


def _handle_password_reset(email: str):
    """Handle password reset request."""
    try:
        client = get_supabase_client()
        client.auth.reset_password_email(email)
        st.success(
            f"Password reset link sent to {email}. "
            "Please check your inbox and follow the instructions."
        )
    except Exception as e:
        st.error(f"Failed to send reset email: {e}")
        logger.error(f"Password reset error: {e}")