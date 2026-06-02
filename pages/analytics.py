"""
Analytics Dashboard
Interview Performance
Aptitude Performance
Resume ATS Progress
Readiness Tracking
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database.interview_queries import (
    get_interview_sessions,
    get_performance_trends
)

from database.resume_queries import (
    get_resume_history
)


def show_analytics(user: dict):

    st.title("📊 Analytics Dashboard")

    user_id = user["id"]

    sessions = get_interview_sessions(
        user_id,
        limit=100
    )

    trends = get_performance_trends(
        user_id
    )

    resumes = get_resume_history(
        user_id
    )

    if not sessions and not resumes:

        st.info(
            "No analytics available yet. Complete interviews or upload a resume."
        )
        return

    show_summary_metrics(
        sessions,
        resumes
    )

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([

        "📈 Performance",
        "🎯 Interview Types",
        "📄 Resume",
        "🧠 Skills",
        "🚀 Readiness"

    ])

    with tab1:
        performance_tab(trends)

    with tab2:
        interview_type_tab(sessions)

    with tab3:
        resume_tab(resumes)

    with tab4:
        skills_tab(sessions)

    with tab5:
        readiness_tab(
            sessions,
            resumes
        )


# --------------------------------------------------
# SUMMARY METRICS
# --------------------------------------------------

def show_summary_metrics(
    sessions,
    resumes
):

    total_interviews = len(
        sessions
    )

    avg_score = round(

        sum(
            s.get("score", 0)
            for s in sessions
        ) /
        max(total_interviews, 1),

        1

    )

    latest_ats = 0

    if resumes:

        latest_ats = resumes[0].get(
            "ats_score",
            0
        )

    best_score = max(

        [
            s.get("score", 0)
            for s in sessions
        ],

        default=0

    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Interviews",
            total_interviews
        )

    with col2:

        st.metric(
            "Average Score",
            f"{avg_score}%"
        )

    with col3:

        st.metric(
            "Best Score",
            f"{best_score}%"
        )

    with col4:

        st.metric(
            "Latest ATS",
            f"{latest_ats}%"
        )


# --------------------------------------------------
# PERFORMANCE TAB
# --------------------------------------------------

def performance_tab(trends):

    st.subheader(
        "Interview Performance Trend"
    )

    if not trends:

        st.info(
            "No interview trend data."
        )
        return

    df = pd.DataFrame(trends)

    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )

    fig = px.line(

        df,

        x="created_at",
        y="score",
        color="interview_type",
        markers=True,

        title="Interview Scores Over Time"

    )

    fig.update_layout(
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# --------------------------------------------------
# INTERVIEW TYPE TAB
# --------------------------------------------------

def interview_type_tab(sessions):

    st.subheader(
        "Interview Type Distribution"
    )

    if not sessions:

        return

    types = {}

    for session in sessions:

        interview_type = session.get(
            "interview_type",
            "Unknown"
        )

        types[interview_type] = (

            types.get(
                interview_type,
                0
            ) + 1

        )

    df = pd.DataFrame({

        "Type":
            list(types.keys()),

        "Count":
            list(types.values())

    })

    fig = px.pie(

        df,

        names="Type",
        values="Count",

        title="Interview Distribution"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("---")

    st.subheader(
        "Average Score by Interview Type"
    )

    score_map = {}

    for session in sessions:

        t = session.get(
            "interview_type",
            "Unknown"
        )

        score_map.setdefault(
            t,
            []
        ).append(
            session.get(
                "score",
                0
            )
        )

    score_df = pd.DataFrame({

        "Type":
            list(score_map.keys()),

        "Score":
            [

                round(
                    sum(v) /
                    len(v),
                    1
                )

                for v in score_map.values()

            ]

    })

    fig = px.bar(

        score_df,

        x="Type",
        y="Score",

        title="Average Score by Type"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# --------------------------------------------------
# RESUME TAB
# --------------------------------------------------

def resume_tab(resumes):

    st.subheader(
        "Resume Progress"
    )

    if not resumes:

        st.info(
            "No resumes uploaded."
        )
        return

    df = pd.DataFrame(resumes)

    if "created_at" in df.columns:

        df["created_at"] = pd.to_datetime(
            df["created_at"]
        )

    fig = px.line(

        df,

        x="created_at",
        y="ats_score",

        markers=True,

        title="ATS Score Progress"

    )

    fig.update_layout(
        height=400
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    latest = resumes[0]

    st.markdown("### Latest Resume")

    st.metric(
        "ATS Score",
        f"{latest.get('ats_score',0)}%"
    )

    st.write(
        latest.get(
            "feedback",
            "No feedback available."
        )
    )


# --------------------------------------------------
# SKILLS TAB
# --------------------------------------------------

def skills_tab(sessions):

    st.subheader(
        "Skill Radar Analysis"
    )

    if not sessions:

        st.info(
            "No skill data available."
        )
        return

    technical = []
    communication = []
    problem_solving = []
    leadership = []
    teamwork = []

    for session in sessions:

        evaluations = session.get(
            "evaluations",
            []
        )

        if not evaluations:
            continue

        for ev in evaluations:

            technical.append(
                ev.get(
                    "technical_accuracy",
                    5
                )
            )

            communication.append(
                ev.get(
                    "communication_clarity",
                    5
                )
            )

            problem_solving.append(
                ev.get(
                    "depth",
                    5
                )
            )

            competencies = ev.get(
                "competencies",
                {}
            )

            leadership.append(
                competencies.get(
                    "leadership",
                    5
                )
            )

            teamwork.append(
                competencies.get(
                    "teamwork",
                    5
                )
            )

    categories = [

        "Technical",
        "Communication",
        "Problem Solving",
        "Leadership",
        "Teamwork"

    ]

    values = [

        average(technical),
        average(communication),
        average(problem_solving),
        average(leadership),
        average(teamwork)

    ]

    fig = go.Figure()

    fig.add_trace(

        go.Scatterpolar(

            r=values,

            theta=categories,

            fill="toself",

            name="Skills"

        )

    )

    fig.update_layout(

        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),

        showlegend=False,

        height=500

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# --------------------------------------------------
# READINESS TAB
# --------------------------------------------------

def readiness_tab(
    sessions,
    resumes
):

    st.subheader(
        "Interview Readiness Score"
    )

    interview_score = average([
        s.get(
            "score",
            0
        )
        for s in sessions
    ])

    ats_score = 0

    if resumes:

        ats_score = resumes[0].get(
            "ats_score",
            0
        )

    readiness = min(

        (
            interview_score * 0.6
            +
            ats_score * 0.4
        ),

        100

    )

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number",

            value=readiness,

            title={
                "text":
                "Readiness Score"
            },

            gauge={

                "axis": {
                    "range":
                    [0, 100]
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

        )

    )

    fig.update_layout(
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    if readiness >= 80:

        st.success(
            "Excellent Interview Readiness 🚀"
        )

    elif readiness >= 60:

        st.info(
            "Good Readiness Level 👍"
        )

    else:

        st.warning(
            "Keep Practicing 📚"
        )


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def average(values):

    if not values:
        return 0

    return round(
        sum(values) / len(values),
        1
    )