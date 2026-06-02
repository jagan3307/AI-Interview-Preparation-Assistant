"""
Reports Page
Interview Reports
ATS Reports
Performance Reports
PDF Export Ready
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from database.interview_queries import (
    get_interview_sessions,
    get_interview_session
)

from database.resume_queries import (
    get_resume_history
)


def show_reports(user: dict):

    st.title("📑 Reports Center")

    user_id = user["id"]

    interviews = get_interview_sessions(
        user_id,
        limit=100
    )

    resumes = get_resume_history(
        user_id
    )

    tab1, tab2, tab3 = st.tabs([

        "🎤 Interview Reports",
        "📄 ATS Reports",
        "📊 Performance Summary"

    ])

    with tab1:
        interview_reports(interviews)

    with tab2:
        ats_reports(resumes)

    with tab3:
        performance_reports(interviews)


# --------------------------------------------------
# INTERVIEW REPORTS
# --------------------------------------------------

def interview_reports(interviews):

    st.subheader("Interview History")

    if not interviews:

        st.info(
            "No interview reports available."
        )
        return

    report_rows = []

    for session in interviews:

        report_rows.append({

            "Date":
                session.get(
                    "created_at",
                    ""
                )[:10],

            "Type":
                session.get(
                    "interview_type",
                    ""
                ),

            "Domain":
                session.get(
                    "domain",
                    ""
                ),

            "Score":
                session.get(
                    "score",
                    0
                ),

            "ID":
                session.get(
                    "id",
                    ""
                )

        })

    df = pd.DataFrame(
        report_rows
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    selected = st.selectbox(

        "Select Session",

        df["ID"].tolist()

    )

    if selected:

        session = get_interview_session(
            selected
        )

        display_session_report(
            session
        )


def display_session_report(session):

    st.markdown("---")

    st.subheader(
        "Detailed Interview Report"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Score",
            f"{session.get('score',0)}%"
        )

    with col2:

        st.metric(
            "Type",
            session.get(
                "interview_type",
                "-"
            )
        )

    with col3:

        st.metric(
            "Domain",
            session.get(
                "domain",
                "-"
            )
        )

    questions = session.get(
        "questions",
        []
    )

    answers = session.get(
        "answers",
        []
    )

    evaluations = session.get(
        "evaluations",
        []
    )

    for i in range(

        min(
            len(questions),
            len(answers)
        )

    ):

        with st.expander(
            f"Question {i+1}"
        ):

            question_text = (
                questions[i].get(
                    "question",
                    str(questions[i])
                )
                if isinstance(
                    questions[i],
                    dict
                )
                else str(
                    questions[i]
                )
            )

            st.markdown(
                f"**Question:** {question_text}"
            )

            st.markdown(
                f"**Answer:** {answers[i]}"
            )

            if i < len(
                evaluations
            ):

                ev = evaluations[i]

                st.success(
                    ev.get(
                        "detailed_feedback",
                        "No feedback"
                    )
                )

                st.write(
                    f"Score: {ev.get('score',0)}/10"
                )


# --------------------------------------------------
# ATS REPORTS
# --------------------------------------------------

def ats_reports(resumes):

    st.subheader(
        "Resume ATS Reports"
    )

    if not resumes:

        st.info(
            "No resume reports available."
        )
        return

    rows = []

    for resume in resumes:

        rows.append({

            "Date":
                resume.get(
                    "created_at",
                    ""
                )[:10],

            "ATS Score":
                resume.get(
                    "ats_score",
                    0
                )

        })

    df = pd.DataFrame(
        rows
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    fig = px.line(

        df,

        x="Date",
        y="ATS Score",

        markers=True,

        title="ATS Improvement Trend"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    latest = resumes[0]

    st.markdown("---")

    st.subheader(
        "Latest ATS Analysis"
    )

    st.metric(
        "ATS Score",
        f"{latest.get('ats_score',0)}%"
    )

    feedback = latest.get(
        "feedback",
        ""
    )

    if feedback:

        st.write(
            feedback
        )


# --------------------------------------------------
# PERFORMANCE REPORTS
# --------------------------------------------------

def performance_reports(interviews):

    st.subheader(
        "Overall Performance Report"
    )

    if not interviews:

        st.info(
            "No performance data."
        )
        return

    scores = [

        session.get(
            "score",
            0
        )

        for session in interviews

    ]

    avg_score = round(

        sum(scores) /
        len(scores),

        1

    )

    best_score = max(
        scores
    )

    worst_score = min(
        scores
    )

    total = len(
        interviews
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Interviews",
            total
        )

    with col2:

        st.metric(
            "Average",
            f"{avg_score}%"
        )

    with col3:

        st.metric(
            "Best",
            f"{best_score}%"
        )

    with col4:

        st.metric(
            "Lowest",
            f"{worst_score}%"
        )

    chart_df = pd.DataFrame({

        "Interview":

            list(
                range(
                    1,
                    total + 1
                )
            ),

        "Score":
            scores[::-1]

    })

    fig = px.line(

        chart_df,

        x="Interview",
        y="Score",

        markers=True,

        title="Performance Progress"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    strengths = []

    weaknesses = []

    for session in interviews:

        evaluations = session.get(
            "evaluations",
            []
        )

        for ev in evaluations:

            if ev.get(
                "score",
                0
            ) >= 8:

                strengths.extend(

                    ev.get(
                        "strengths",
                        []
                    )

                )

            if ev.get(
                "score",
                0
            ) <= 5:

                weaknesses.extend(

                    ev.get(
                        "improvements",
                        []
                    )

                )

    st.markdown("---")

    st.subheader(
        "Top Strengths"
    )

    if strengths:

        for item in strengths[:10]:

            st.success(
                item
            )

    st.subheader(
        "Improvement Areas"
    )

    if weaknesses:

        for item in weaknesses[:10]:

            st.warning(
                item
            )

    create_download_report(
        interviews,
        avg_score,
        best_score
    )


# --------------------------------------------------
# DOWNLOAD REPORT
# --------------------------------------------------

def create_download_report(

    interviews,
    avg_score,
    best_score

):

    report_text = f"""
AI INTERVIEW PREPARATION REPORT

Total Interviews:
{len(interviews)}

Average Score:
{avg_score}%

Best Score:
{best_score}%

Generated by AI Interview Preparation Assistant
"""

    st.download_button(

        label="⬇️ Download Report",

        data=report_text,

        file_name="interview_report.txt",

        mime="text/plain"

    )
