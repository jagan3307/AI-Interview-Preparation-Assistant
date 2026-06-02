"""
Settings Page
"""

import streamlit as st


def show_settings(user):

    st.title("⚙️ Settings")

    st.subheader(
        "Interview Preferences"
    )

    difficulty = st.selectbox(

        "Default Difficulty",

        [

            "Easy",
            "Medium",
            "Hard"

        ]

    )

    language = st.selectbox(

        "Preferred Language",

        [

            "English",
            "Tamil",
            "Hindi"

        ]

    )

    voice_enabled = st.toggle(
        "Enable Voice Interview"
    )

    st.markdown("---")

    st.subheader(
        "Notifications"
    )

    email_notifications = st.checkbox(
        "Email Notifications"
    )

    weekly_reports = st.checkbox(
        "Weekly Progress Reports"
    )

    st.markdown("---")

    st.subheader(
        "Theme"
    )

    theme = st.radio(

        "Theme",

        [

            "Light",
            "Dark"

        ]

    )

    if st.button(
        "💾 Save Settings",
        use_container_width=True
    ):

        st.success(
            "Settings Saved Successfully"
        )

        st.session_state.settings = {

            "difficulty":
                difficulty,

            "language":
                language,

            "voice_enabled":
                voice_enabled,

            "email_notifications":
                email_notifications,

            "weekly_reports":
                weekly_reports,

            "theme":
                theme

        }
