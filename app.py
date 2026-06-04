"""
AI Interview Preparation Assistant
Main Application Entry Point
"""

import streamlit as st
import os
import sys


# ---------------------------------------------------
# PROJECT ROOT
# ---------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_CONFIG

from auth.session import (
    init_session,
    get_current_user,
    logout
)

from auth.login import show_login_page
from auth.signup import show_signup_page
from auth.forgot_password import show_forgot_password_page

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title=APP_CONFIG.get("app_name", "AI Interview Assistant"),
    page_icon=APP_CONFIG.get("app_icon", "🎯"),
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# HIDE STREAMLIT DEFAULT PAGES MENU
# ---------------------------------------------------
st.markdown("""
<style>

/* Hide Streamlit multipage navigation */
[data-testid="stSidebarNav"] {
    display: none;
}

/* Hide default page list */
section[data-testid="stSidebar"] div[data-testid="stSidebarNav"] {
    display: none;
}

/* Remove top padding */
.block-container {
    padding-top: 1rem;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD CUSTOM CSS
# ---------------------------------------------------
def load_css():
    css_file = os.path.join("assets", "styles.css")

    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )

load_css()

# ---------------------------------------------------
# MAIN
# ---------------------------------------------------
def main():

    init_session()

    # Restore Google OAuth session
    try:
        from database.supabase_client import get_supabase_client
        from auth.session import set_user
        from database.user_queries import (
            get_user_profile,
            create_user_profile
        )

        client = get_supabase_client()

        session = client.auth.get_session()

        if (
            session
            and session.session
            and not st.session_state.get("user")
        ):

            auth_user = session.session.user

            profile = get_user_profile(auth_user.id)

            if not profile:

                profile = create_user_profile(
                    user_id=auth_user.id,
                    email=auth_user.email,
                    full_name=auth_user.user_metadata.get(
                        "full_name",
                        auth_user.email.split("@")[0]
                    )
                )

            user_data = {
                "id": auth_user.id,
                "email": auth_user.email,
                "full_name": profile.get(
                    "full_name",
                    auth_user.user_metadata.get(
                        "full_name",
                        auth_user.email.split("@")[0]
                    )
                ),
                "is_admin": profile.get(
                    "is_admin",
                    False
                ),
                **profile
            }

            set_user(user_data)

    except Exception as e:
        print("OAuth Restore Error:", e)

    user = get_current_user()

    if not user:

        if "auth_page" not in st.session_state:
            st.session_state.auth_page = "login"

        if st.session_state.auth_page == "login":
            show_login_page()

        elif st.session_state.auth_page == "signup":
            show_signup_page()

        elif st.session_state.auth_page == "forgot_password":
            show_forgot_password_page()

        return

    show_main_app(user)
# ---------------------------------------------------
def show_main_app(user):

    # Lazy imports
    from pages.dashboard import show_dashboard
    from pages.profile import show_profile
    from pages.resume_analyzer import show_resume_analyzer
    from pages.technical_interview import show_technical_interview
    from pages.coding_interview import show_coding_interview
    from pages.non_technical_interview import show_non_technical_interview
    from pages.hr_interview import show_hr_interview
    from pages.aptitude_test import show_aptitude_test
    from pages.voice_interview import show_voice_interview
    from pages.company_preparation import show_company_preparation
    from pages.analytics import show_analytics
    from pages.reports import show_reports
    from pages.settings import show_settings
    from pages.chatbot import show_chatbot

    # ---------------------------------------------------
    # PAGE ROUTING
    # ---------------------------------------------------
    page_map = {
        "dashboard": show_dashboard,
        "profile": show_profile,
        "resume_analyzer": show_resume_analyzer,
        "technical_interview": show_technical_interview,
        "coding_interview": show_coding_interview,
        "non_technical": show_non_technical_interview,
        "hr_interview": show_hr_interview,
        "aptitude_test": show_aptitude_test,
        "voice_interview": show_voice_interview,
        "company_prep": show_company_preparation,
        "analytics": show_analytics,
        "reports": show_reports,
        "settings": show_settings,
        "chatbot": show_chatbot,
    }

    # ---------------------------------------------------
    # DEFAULT PAGE
    # ---------------------------------------------------
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

    # ---------------------------------------------------
    # SIDEBAR
    # ---------------------------------------------------
    with st.sidebar:

        if os.path.exists("assets/logo.png"):
            st.image("assets/logo.png", width=180)

        st.markdown("## 🎯 AI Interview Assistant")

        st.markdown(
            f"""
            Welcome,

            **{user.get('full_name', user.get('email', 'User'))}**
            """
        )

        st.divider()

        navigation = {
            "🏠 Dashboard": "dashboard",
            "👤 Profile": "profile",
            "📄 Resume Analyzer": "resume_analyzer",
            "🤖 AI Chatbot": "chatbot",
            "💻 Technical Interview": "technical_interview",
            "🖥️ Coding Interview": "coding_interview",
            "🗣️ Non Technical": "non_technical",
            "🤝 HR Interview": "hr_interview",
            "🧮 Aptitude Test": "aptitude_test",
            "🎙️ Voice Interview": "voice_interview",
            "🏢 Company Prep": "company_prep",
            "📊 Analytics": "analytics",
            "📋 Reports": "reports",
            "⚙️ Settings": "settings"
        }

        for label, page_key in navigation.items():

            if st.button(
                label,
                key=page_key,
                use_container_width=True,
                type="primary" if st.session_state.current_page == page_key else "secondary"
            ):
                st.session_state.current_page = page_key
                st.rerun()

        st.divider()

        if user.get("is_admin", False):

            if st.button(
                "🔧 Admin Panel",
                use_container_width=True
            ):
                st.session_state.current_page = "admin"
                st.rerun()

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):
            logout()
            st.rerun()

    # ---------------------------------------------------
    # PAGE DISPLAY
    # ---------------------------------------------------
    page = st.session_state.current_page

    try:

        if page == "admin" and user.get("is_admin", False):
            from admin.dashboard import show_admin_dashboard
            show_admin_dashboard(user)

        elif page in page_map:
            page_map[page](user)

        else:
            show_dashboard(user)

    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.exception(e)

# ---------------------------------------------------
# RUN APP
# ---------------------------------------------------
if __name__ == "__main__":
    main()