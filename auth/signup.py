"""
Signup Page - New user registration
"""

import streamlit as st
from auth.session import set_user
from database.supabase_client import get_supabase_client
from database.user_queries import create_user_profile
import re
import logging

logger = logging.getLogger(__name__)


def show_signup_page():
    """Display the signup page."""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            """
            <div style='text-align: center; padding: 1rem 0'>
                <h1>🎯 Create Account</h1>
                <p style='color: #666'>Start your interview preparation journey</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        with st.form("signup_form"):
            full_name = st.text_input("👤 Full Name", placeholder="John Doe")
            email = st.text_input("📧 Email", placeholder="your@email.com")
            password = st.text_input("🔒 Password", type="password", placeholder="Min 8 characters")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Repeat password")
            
            st.markdown("**Your background (optional)**")
            col_a, col_b = st.columns(2)
            with col_a:
                experience_level = st.selectbox("Experience Level", [
                    "Student", "Fresher", "1-2 Years", "3-5 Years", "5+ Years"
                ])
            with col_b:
                target_role = st.text_input("Target Role", placeholder="e.g. Software Engineer")
            
            agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            col_x, col_y = st.columns(2)
            with col_x:
                submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            with col_y:
                back = st.form_submit_button("Back to Login", use_container_width=True)
            
            if submit:
                _handle_signup(full_name, email, password, confirm_password, agree, {
                    "experience_level": experience_level,
                    "target_role": target_role,
                })
            
            if back:
                st.session_state.auth_page = "login"
                st.rerun()


def _handle_signup(full_name, email, password, confirm_password, agree, extra_info):
    """Handle user registration."""
    # Validation
    errors = []
    
    if not full_name.strip():
        errors.append("Full name is required.")
    
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append("Valid email is required.")
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    
    if password != confirm_password:
        errors.append("Passwords do not match.")
    
    if not agree:
        errors.append("Please agree to the Terms of Service.")
    
    if errors:
        for error in errors:
            st.error(error)
        return
    
    try:
        client = get_supabase_client()
        response = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"full_name": full_name}
            }
        })
        
        if response.user:
            # Create profile
            profile_data = {
                "experience_level": extra_info.get("experience_level", ""),
                "target_role": extra_info.get("target_role", ""),
                "profile_completed": bool(extra_info.get("target_role")),
            }

            create_user_profile(
                user_id=response.user.id,
                email=email,
                full_name=full_name,
                **profile_data
            )
            
            if response.session:
                # Auto-login if session returned
                user_data = {
                    "id": response.user.id,
                    "email": email,
                    "full_name": full_name,
                    "is_admin": False,
                    **profile_data,
                }
                set_user(user_data, response.session.access_token)
                st.success(f"Welcome to AI Interview Assistant, {full_name}!")
                st.rerun()
            else:
                st.success(
                    "Account created! Please check your email to confirm your account, then log in."
                )
                st.session_state.auth_page = "login"
                st.rerun()
        else:
            st.error("Registration failed. Please try again.")
    
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            st.error("This email is already registered. Please log in.")
        else:
            st.error(f"Registration failed: {error_msg}")
            logger.error(f"Signup error: {e}")