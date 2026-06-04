"""
Login Page - Email/password and Google OAuth login
"""

import streamlit as st
from auth.session import set_user
from database.supabase_client import get_supabase_client
from database.user_queries import get_user_profile, create_user_profile
import logging

logger = logging.getLogger(__name__)


def show_login_page():
    """Display the login page."""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            """
            <div style='text-align: center; padding: 2rem 0'>
                <h1 style='font-size: 2.5rem'>🎯 AI Interview Assistant</h1>
                <p style='color: #666; font-size: 1.1rem'>Your AI-powered interview preparation platform</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown("### Sign In")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="your@email.com")
            password = st.text_input("🔒 Password", type="password", placeholder="Your password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            with col_b:
                forgot = st.form_submit_button("Forgot Password?", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("Please enter your email and password.")
                else:
                    _handle_login(email, password)
            
            if forgot:
                st.session_state.auth_page = "forgot_password"
                st.rerun()
        
        st.markdown("---")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📝 Create Account", use_container_width=True):
                st.session_state.auth_page = "signup"
                st.rerun()
        with col_b:
            if st.button("🔑 Google Sign In", use_container_width=True):
                _handle_google_login()
        
        # Demo account info
        with st.expander("💡 Demo Account"):
            st.info(
                "Email: sam123@gmail.com\n"
                "Password: qwer@1234\n\n"
                "Or create a free account to get started!"
            )


def _handle_login(email: str, password: str):
    """Handle email/password login."""
    try:
        client = get_supabase_client()
        response = client.auth.sign_in_with_password({"email": email, "password": password})
        
        if response.user:
            user_id = response.user.id
            profile = get_user_profile(user_id)
            
            if not profile:
                # Create profile if doesn't exist
                profile = create_user_profile(
                    user_id=user_id,
                    email=email,
                    full_name=response.user.user_metadata.get("full_name", ""),
                )
            
            user_data = {
                "id": user_id,
                "email": email,
                "full_name": profile.get("full_name", email.split("@")[0]),
                "is_admin": profile.get("is_admin", False),
                **profile,
            }
            
            set_user(user_data, response.session.access_token if response.session else None)
            st.success(f"Welcome back, {user_data['full_name']}!")
            st.rerun()
        else:
            st.error("Invalid email or password. Please try again.")
    
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            st.error("Invalid email or password.")
        elif "Email not confirmed" in error_msg:
            st.warning("Please confirm your email address before logging in.")
        else:
            st.error(f"Login failed: {error_msg}")
            logger.error(f"Login error: {e}")


def _handle_google_login():

    try:

        client = get_supabase_client()

        response = client.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {
                    "redirect_to":
                    "https://ai-interview-preparation-assistant007.streamlit.app"
                }
            }
        )

        st.link_button(
            "Continue with Google",
            response.url,
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Google login failed: {e}")
        logger.error(f"Google OAuth error: {e}")