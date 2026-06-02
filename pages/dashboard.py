"""
Dashboard Page - Main overview with stats and quick actions
"""

import streamlit as st
from database.user_queries import get_user_stats
from database.interview_queries import get_interview_sessions, get_performance_trends
from database.resume_queries import get_latest_resume
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta


def show_dashboard(user: dict):
    """Display the main dashboard."""
    st.title(f"🏠 Dashboard")
    st.markdown(f"Welcome back, **{user.get('full_name', 'User')}**! Ready to ace your next interview?")
    
    user_id = user["id"]
    
    # Stats row
    stats = get_user_stats(user_id)
    recent_sessions = get_interview_sessions(user_id, limit=10)
    latest_resume = get_latest_resume(user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Total Interviews",
            stats.get("total_interviews", 0),
            delta="+2 this week" if stats.get("total_interviews", 0) > 2 else None,
        )
    with col2:
        avg_score = stats.get("average_score", 0)
        st.metric(
            "📊 Avg Score",
            f"{avg_score:.0f}%",
            delta="+5%" if avg_score > 50 else None,
        )
    with col3:
        st.metric(
            "📄 Resumes Analyzed",
            stats.get("resumes_uploaded", 0),
        )
    with col4:
        ats_score = latest_resume.get("ats_score", 0) if latest_resume else 0
        st.metric(
            "🤖 ATS Score",
            f"{ats_score}%",
            delta="Latest resume" if ats_score else None,
        )
    
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 Performance Trends")
        if recent_sessions:
            df = pd.DataFrame([{
                "Date": s.get("created_at", "")[:10],
                "Score": s.get("score", 0),
                "Type": s.get("interview_type", "").replace("_", " ").title(),
            } for s in recent_sessions[:10]])
            
            fig = px.line(
                df, x="Date", y="Score", color="Type",
                title="Interview Scores Over Time",
                markers=True,
            )
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Complete your first interview to see performance trends here!")
            _show_empty_chart()
    
    with col_right:
        st.subheader("🎯 Quick Actions")
        
        actions = [
            ("📄 Analyze Resume", "resume_analyzer"),
            ("💻 Technical Interview", "technical_interview"),
            ("🤝 HR Interview", "hr_interview"),
            ("🧮 Aptitude Test", "aptitude_test"),
            ("🏢 Company Prep", "company_prep"),
            ("📊 View Analytics", "analytics"),
        ]
        
        for label, page in actions:
            if st.button(label, use_container_width=True, key=f"quick_{page}"):
                st.session_state.current_page = page
                st.rerun()
    
    st.markdown("---")
    
    # Recent activity
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🕐 Recent Interviews")
        if recent_sessions:
            for session in recent_sessions[:5]:
                with st.container():
                    score = session.get("score", 0)
                    score_color = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                    st.markdown(
                        f"{score_color} **{session.get('interview_type', 'Interview').replace('_', ' ').title()}** "
                        f"— {session.get('domain', 'General')} "
                        f"| Score: **{score}%** "
                        f"| {session.get('created_at', '')[:10]}"
                    )
        else:
            st.info("No interviews yet. Start your first mock interview!")
    
    with col_b:
        st.subheader("💡 Preparation Tips")
        tips = [
            "🎯 Practice answering using the STAR method for behavioral questions",
            "💡 Review Data Structures & Algorithms daily for 30 minutes",
            "📝 Tailor your resume keywords to match job descriptions",
            "🔊 Practice speaking answers out loud to improve confidence",
            "🏢 Research company culture before company-specific prep",
        ]
        for tip in tips:
            st.markdown(f"• {tip}")
    
    # Interview readiness gauge
    st.markdown("---")
    st.subheader("🎯 Overall Interview Readiness")
    
    readiness = _calculate_readiness(stats, latest_resume)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=readiness,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Readiness Score"},
            delta={"reference": 60},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#00b4d8"},
                "steps": [
                    {"range": [0, 40], "color": "#ff6b6b"},
                    {"range": [40, 70], "color": "#ffd93d"},
                    {"range": [70, 100], "color": "#6bcb77"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 70,
                },
            },
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)


def _show_empty_chart():
    """Show placeholder chart."""
    fig = go.Figure()
    fig.add_annotation(
        text="No data yet — start practicing!",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color="gray"),
    )
    fig.update_layout(height=300, xaxis={"visible": False}, yaxis={"visible": False})
    st.plotly_chart(fig, use_container_width=True)


def _calculate_readiness(stats: dict, resume: dict) -> int:
    """Calculate overall interview readiness score."""
    score = 0
    
    interviews = stats.get("total_interviews", 0)
    score += min(interviews * 10, 30)
    
    avg = stats.get("average_score", 0)
    score += min(avg * 0.3, 30)
    
    ats = resume.get("ats_score", 0) if resume else 0
    score += min(ats * 0.2, 20)
    
    if resume:
        score += 20
    
    return min(int(score), 100)