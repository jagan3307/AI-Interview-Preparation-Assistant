"""
Resume Analyzer Page - Upload and analyze resumes
"""

import streamlit as st
from resume.pdf_parser import parse_pdf_resume
from resume.docx_parser import parse_docx_resume
from resume.ats_scorer import calculate_ats_score
from ai.resume_analyzer import extract_resume_info, analyze_resume
from database.resume_queries import save_resume_analysis, get_resume_analyses
import plotly.graph_objects as go
import plotly.express as px


def show_resume_analyzer(user: dict):
    """Display the resume analyzer page."""
    st.title("📄 Resume Analyzer")
    st.markdown("Upload your resume to get AI-powered analysis, ATS score, and improvement suggestions.")
    
    tab1, tab2 = st.tabs(["📤 Analyze New Resume", "📚 Previous Analyses"])
    
    with tab1:
        _show_upload_section(user)
    
    with tab2:
        _show_history(user)


def _show_upload_section(user: dict):
    """Show resume upload and analysis section."""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Resume")
        
        uploaded_file = st.file_uploader(
            "Choose your resume",
            type=["pdf", "docx", "doc"],
            help="Supports PDF and Word documents. Max size: 10MB",
        )
        
        target_job = st.text_input(
            "🎯 Target Job Title (optional)",
            placeholder="e.g. Senior Software Engineer",
            help="Helps generate more targeted recommendations",
        )
        
        if uploaded_file and st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
            _analyze_resume(user, uploaded_file, target_job)
    
    with col2:
        st.subheader("ℹ️ What we analyze")
        features = [
            ("🤖 ATS Score", "Check how well your resume passes ATS filters"),
            ("📊 Content Analysis", "Evaluate quality and completeness"),
            ("🔑 Keywords", "Find missing important keywords"),
            ("💪 Strengths", "Identify what's working well"),
            ("⚠️ Weaknesses", "Areas that need improvement"),
            ("✅ Suggestions", "Actionable improvement tips"),
            ("🎓 Certifications", "Recommended certifications to add value"),
            ("💼 Projects", "Project ideas to strengthen your profile"),
        ]
        for icon_title, description in features:
            st.markdown(f"**{icon_title}** — {description}")
    
    # Show current analysis if in session
    if st.session_state.get("current_resume_analysis"):
        _display_analysis(st.session_state.current_resume_analysis)


def _analyze_resume(user: dict, uploaded_file, target_job: str = ""):
    """Process and analyze uploaded resume."""
    
    with st.spinner("📖 Reading resume..."):
        file_bytes = uploaded_file.read()
        
        if uploaded_file.name.endswith(".pdf"):
            resume_text = parse_pdf_resume(file_bytes)
        else:
            resume_text = parse_docx_resume(file_bytes)
        
        if not resume_text.strip():
            st.error("Could not extract text from your resume. Please ensure it's not scanned/image-based.")
            return
    
    with st.spinner("🤖 Extracting information..."):
        extracted_info = extract_resume_info(resume_text)
    
    with st.spinner("📊 Analyzing ATS compatibility..."):
        ats_data = calculate_ats_score(resume_text, extracted_info)
    
    with st.spinner("🔍 Generating AI analysis..."):
        ai_analysis = analyze_resume(resume_text, extracted_info)
    
    # Combine all data
    full_analysis = {
        "filename": uploaded_file.name,
        "raw_text": resume_text,
        "extracted_info": extracted_info,
        "ats_score": ai_analysis.get("ats_score", ats_data["overall"]),
        "ats_breakdown": ai_analysis.get("ats_breakdown", ats_data),
        "strengths": ai_analysis.get("strengths", []),
        "weaknesses": ai_analysis.get("weaknesses", []),
        "suggestions": ai_analysis.get("improvement_suggestions", []),
        "missing_keywords": ai_analysis.get("missing_keywords", []),
        "recommended_certifications": ai_analysis.get("recommended_certifications", []),
        "recommended_projects": ai_analysis.get("recommended_projects", []),
        "overall_assessment": ai_analysis.get("overall_assessment", ""),
        "interview_readiness": ai_analysis.get("interview_readiness", 0),
        "target_job": target_job,
    }
    
    # Save to database
    save_resume_analysis(user["id"], full_analysis)
    
    # Store in session
    st.session_state.current_resume_analysis = full_analysis
    st.session_state.resume_data = {
        "extracted_info": extracted_info,
        "text": resume_text,
    }
    
    st.success("✅ Resume analyzed successfully!")
    _display_analysis(full_analysis)


def _display_analysis(analysis: dict):
    """Display resume analysis results."""
    st.markdown("---")
    st.subheader("📊 Analysis Results")
    
    # ATS Score prominent display
    ats_score = analysis.get("ats_score", 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🤖 ATS Score", f"{ats_score}%")
    with col2:
        st.metric("🎯 Interview Readiness", f"{analysis.get('interview_readiness', 0)}%")
    with col3:
        extracted = analysis.get("extracted_info", {})
        skill_count = sum(len(v) for v in extracted.get("skills", {}).values() if isinstance(v, list))
        st.metric("💡 Skills Found", skill_count)
    
    # ATS gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ats_score,
        title={"text": "ATS Compatibility Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#00b4d8"},
            "steps": [
                {"range": [0, 40], "color": "#ff6b6b"},
                {"range": [40, 70], "color": "#ffd93d"},
                {"range": [70, 100], "color": "#6bcb77"},
            ],
        },
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=10))
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        # ATS breakdown
        breakdown = analysis.get("ats_breakdown", {})
        if breakdown:
            cats = ["Keywords", "Formatting", "Content Quality", "Completeness"]
            vals = [
                breakdown.get("keywords", 0),
                breakdown.get("formatting", 0),
                breakdown.get("content_quality", 0),
                breakdown.get("completeness", 0),
            ]
            fig2 = px.bar(
                x=cats, y=vals,
                title="ATS Score Breakdown",
                color=vals,
                color_continuous_scale="RdYlGn",
                range_color=[0, 100],
            )
            fig2.update_layout(height=250, showlegend=False, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig2, use_container_width=True)
    
    # Overall assessment
    if analysis.get("overall_assessment"):
        st.info(f"**📋 Assessment:** {analysis['overall_assessment']}")
    
    # Tabs for detailed analysis
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 Extracted Info", "💪 Strengths & Gaps", "🔑 Keywords", "✅ Suggestions", "🎓 Recommendations"
    ])
    
    with tab1:
        _show_extracted_info(analysis.get("extracted_info", {}))
    
    with tab2:
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("### ✅ Strengths")
            for s in analysis.get("strengths", []):
                st.markdown(f"• {s}")
        with col_w:
            st.markdown("### ⚠️ Weaknesses")
            for w in analysis.get("weaknesses", []):
                st.markdown(f"• {w}")
    
    with tab3:
        st.markdown("### 🔍 Missing Keywords")
        st.markdown("Add these keywords to improve ATS compatibility:")
        cols = st.columns(3)
        for i, kw in enumerate(analysis.get("missing_keywords", [])[:15]):
            with cols[i % 3]:
                st.markdown(f"• `{kw}`")
    
    with tab4:
        st.markdown("### 💡 Improvement Suggestions")
        for suggestion in analysis.get("suggestions", []):
            if isinstance(suggestion, dict):
                priority = suggestion.get("priority", "medium")
                icon = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                st.markdown(f"{icon} **{suggestion.get('area', '')}**: {suggestion.get('suggestion', '')}")
            else:
                st.markdown(f"• {suggestion}")
    
    with tab5:
        col_c, col_p = st.columns(2)
        with col_c:
            st.markdown("### 🎓 Recommended Certifications")
            for cert in analysis.get("recommended_certifications", []):
                st.markdown(f"• {cert}")
        with col_p:
            st.markdown("### 💼 Recommended Projects")
            for proj in analysis.get("recommended_projects", []):
                st.markdown(f"• {proj}")
    
    # Generate interview questions button
    st.markdown("---")
    if st.button("🎯 Generate Interview Questions from Resume", type="primary", use_container_width=True):
        st.session_state.current_page = "technical_interview"
        st.session_state.use_resume_questions = True
        st.rerun()


def _show_extracted_info(info: dict):
    """Display extracted resume information."""
    if not info:
        st.info("No information extracted.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Personal Info**")
        st.markdown(f"👤 Name: {info.get('name', 'Not found')}")
        st.markdown(f"📧 Email: {info.get('email', 'Not found')}")
        st.markdown(f"📱 Phone: {info.get('phone', 'Not found')}")
        st.markdown(f"📍 Location: {info.get('location', 'Not found')}")
        if info.get("linkedin"):
            st.markdown(f"💼 LinkedIn: {info['linkedin']}")
        if info.get("github"):
            st.markdown(f"🐱 GitHub: {info['github']}")
        
        st.markdown("**Education**")
        for edu in info.get("education", [])[:3]:
            st.markdown(f"🎓 {edu.get('degree', '')} — {edu.get('institution', '')} ({edu.get('year', '')})")
    
    with col2:
        st.markdown("**Skills**")
        skills = info.get("skills", {})
        for category, items in skills.items():
            if items and isinstance(items, list):
                st.markdown(f"**{category.title()}:** {', '.join(items[:8])}")
        
        st.markdown("**Projects**")
        for proj in info.get("projects", [])[:3]:
            tech = ", ".join(proj.get("technologies", [])[:4])
            st.markdown(f"🚀 **{proj.get('name', '')}** — {tech}")
        
        st.markdown("**Certifications**")
        for cert in info.get("certifications", [])[:5]:
            st.markdown(f"🏆 {cert.get('name', '')} — {cert.get('issuer', '')}")


def _show_history(user: dict):
    """Show previous resume analyses."""
    analyses = get_resume_analyses(user["id"])
    
    if not analyses:
        st.info("No previous analyses. Upload a resume to get started!")
        return
    
    st.subheader(f"📚 {len(analyses)} Previous Analyses")
    
    for analysis in analyses:
        with st.expander(
            f"📄 {analysis.get('filename', 'Resume')} — "
            f"ATS: {analysis.get('ats_score', 0)}% — "
            f"{analysis.get('created_at', '')[:10]}"
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ATS Score", f"{analysis.get('ats_score', 0)}%")
            with col2:
                strengths = analysis.get("strengths", [])
                st.metric("Strengths Found", len(strengths))
            with col3:
                suggestions = analysis.get("suggestions", [])
                st.metric("Suggestions", len(suggestions))
            
            if st.button("View Full Analysis", key=f"view_{analysis.get('id', '')}"):
                st.session_state.current_resume_analysis = analysis
                st.rerun()