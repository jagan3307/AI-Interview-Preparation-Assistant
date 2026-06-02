"""
Company Specific Interview Preparation
Google, Amazon, Microsoft, TCS, Infosys, etc.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from ai.question_generator import generate_company_questions
from database.interview_queries import save_interview_session


COMPANIES = [
    "Google",
    "Microsoft",
    "Amazon",
    "Meta",
    "Apple",
    "Netflix",
    "TCS",
    "Infosys",
    "Wipro",
    "Accenture",
    "Cognizant",
    "Capgemini",
    "HCL",
    "Zoho"
]

ROLES = [
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "Business Analyst",
    "DevOps Engineer",
    "Cloud Engineer"
]


def show_company_preparation(user: dict):

    st.title("🏢 Company Interview Preparation")

    initialize_state()

    if not st.session_state.company_loaded:
        setup_company_prep()
    else:
        display_company_content(user)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

def initialize_state():

    defaults = {

        "company_loaded": False,
        "company_name": "",
        "company_role": "",
        "company_data": {},
        "company_start_time": None

    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

def setup_company_prep():

    st.subheader("Select Target Company")

    company = st.selectbox(
        "Company",
        COMPANIES
    )

    role = st.selectbox(
        "Role",
        ROLES
    )

    if st.button(
        "🚀 Generate Preparation Plan",
        use_container_width=True
    ):

        with st.spinner(
            "Generating company-specific preparation material..."
        ):

            company_data = generate_company_questions(
                company=company,
                role=role,
                num_questions=10
            )

        if not company_data:

            st.error(
                "Unable to generate company preparation data."
            )
            return

        st.session_state.company_name = company
        st.session_state.company_role = role
        st.session_state.company_data = company_data
        st.session_state.company_loaded = True
        st.session_state.company_start_time = datetime.now()

        st.rerun()


# --------------------------------------------------
# MAIN CONTENT
# --------------------------------------------------

def display_company_content(user):

    company = st.session_state.company_name
    role = st.session_state.company_role
    data = st.session_state.company_data

    st.success(
        f"Preparation Plan for {company} - {role}"
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([

        "📌 Overview",
        "🧠 Questions",
        "💡 Tips",
        "⚠️ Mistakes",
        "📊 Readiness"

    ])

    with tab1:
        show_overview(data)

    with tab2:
        show_questions(data)

    with tab3:
        show_tips(data)

    with tab4:
        show_mistakes(data)

    with tab5:
        show_readiness(data)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💾 Save Preparation Session",
            use_container_width=True
        ):
            save_session(user)

    with col2:

        if st.button(
            "🔄 New Company",
            use_container_width=True
        ):
            reset_company_prep()
            st.rerun()


# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

def show_overview(data):

    st.subheader("Company Overview")

    st.write(
        data.get(
            "company_overview",
            "No company overview available."
        )
    )

    st.markdown("### Interview Process")

    process = data.get(
        "interview_process",
        []
    )

    if process:

        for i, step in enumerate(process, start=1):

            st.markdown(
                f"**Round {i}:** {step}"
            )

    st.markdown("### Key Focus Areas")

    focus_areas = data.get(
        "key_focus_areas",
        []
    )

    for area in focus_areas:

        st.success(area)


# --------------------------------------------------
# QUESTIONS
# --------------------------------------------------

def show_questions(data):

    st.subheader(
        "Frequently Asked Questions"
    )

    questions = data.get(
        "questions",
        []
    )

    if not questions:

        st.warning(
            "No questions available."
        )
        return

    for i, q in enumerate(
        questions,
        start=1
    ):

        with st.expander(
            f"Question {i}"
        ):

            st.markdown(
                f"### {q.get('question')}"
            )

            st.write(
                f"**Category:** {q.get('category','N/A')}"
            )

            st.write(
                f"**Difficulty:** {q.get('difficulty','N/A')}"
            )

            st.info(
                q.get(
                    "why_asked",
                    "No explanation available."
                )
            )


# --------------------------------------------------
# TIPS
# --------------------------------------------------

def show_tips(data):

    st.subheader("Preparation Tips")

    tips = data.get(
        "preparation_tips",
        []
    )

    if not tips:

        st.info("No tips available.")
        return

    for tip in tips:

        st.success(
            f"✅ {tip}"
        )

    st.markdown("### Recommended Resources")

    resources = data.get(
        "resources",
        []
    )

    for resource in resources:

        st.write(
            f"📚 {resource}"
        )


# --------------------------------------------------
# MISTAKES
# --------------------------------------------------

def show_mistakes(data):

    st.subheader(
        "Common Mistakes"
    )

    mistakes = data.get(
        "common_mistakes",
        []
    )

    if not mistakes:

        st.info(
            "No common mistakes available."
        )
        return

    for mistake in mistakes:

        st.error(
            f"❌ {mistake}"
        )


# --------------------------------------------------
# READINESS DASHBOARD
# --------------------------------------------------

def show_readiness(data):

    focus = len(
        data.get(
            "key_focus_areas",
            []
        )
    )

    questions = len(
        data.get(
            "questions",
            []
        )
    )

    tips = len(
        data.get(
            "preparation_tips",
            []
        )
    )

    readiness = min(
        (
            focus * 10 +
            questions * 3 +
            tips * 2
        ),
        100
    )

    fig = go.Figure(go.Indicator(

        mode="gauge+number",

        value=readiness,

        title={
            "text":
            "Interview Readiness"
        },

        gauge={

            "axis": {
                "range": [0, 100]
            },

            "steps": [

                {
                    "range": [0, 40],
                    "color": "#ff6b6b"
                },

                {
                    "range": [40, 70],
                    "color": "#ffd93d"
                },

                {
                    "range": [70, 100],
                    "color": "#6bcb77"
                }

            ]

        }

    ))

    fig.update_layout(
        height=400
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    if readiness >= 80:

        st.success(
            "Excellent preparation level."
        )

    elif readiness >= 60:

        st.info(
            "Good preparation level."
        )

    else:

        st.warning(
            "More preparation recommended."
        )


# --------------------------------------------------
# SAVE SESSION
# --------------------------------------------------

def save_session(user):

    duration = (

        datetime.now()
        -
        st.session_state.company_start_time

    )

    session_data = {

        "type":
            "company_preparation",

        "domain":
            st.session_state.company_role,

        "difficulty":
            "Medium",

        "questions":
            st.session_state.company_data.get(
                "questions",
                []
            ),

        "answers":
            [],

        "evaluations":
            [],

        "score":
            0,

        "feedback":
            "Company Preparation Session",

        "duration":
            int(
                duration.total_seconds() / 60
            ),

        "company":
            st.session_state.company_name

    }

    session_id = save_interview_session(

        user["id"],
        session_data

    )

    if session_id:

        st.success(
            "Preparation session saved."
        )

    else:

        st.error(
            "Unable to save session."
        )


# --------------------------------------------------
# RESET
# --------------------------------------------------

def reset_company_prep():

    keys = [

        "company_loaded",
        "company_name",
        "company_role",
        "company_data",
        "company_start_time"

    ]

    for key in keys:

        if key in st.session_state:
            del st.session_state[key]

