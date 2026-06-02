"""
HR Interview Simulator Page
"""

import streamlit as st
from ai.question_generator import generate_hr_questions
from ai.answer_evaluator import evaluate_hr_answer, calculate_session_score
from ai.followup_generator import generate_followup
from ai.feedback_generator import generate_session_feedback
from database.interview_queries import save_interview_session
import plotly.graph_objects as go


def show_hr_interview(user: dict):
    """Display the HR interview simulator page."""
    st.title("🤝 HR Interview Simulator")
    st.markdown("Practice behavioral and HR interviews with STAR method analysis.")
    
    if "hr_interview_state" not in st.session_state:
        st.session_state.hr_interview_state = "setup"
    
    state = st.session_state.hr_interview_state
    
    if state == "setup":
        _show_hr_setup()
    elif state == "interviewing":
        _show_hr_interview(user)
    elif state == "results":
        _show_hr_results(user)


def _show_hr_setup():
    """Show HR interview setup."""
    st.subheader("⚙️ Configure HR Interview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        interview_context = st.text_area(
            "🏢 Interview Context (optional)",
            placeholder="e.g. Applying for Senior Software Engineer at Google. 3 years experience in Python and ML.",
            height=100,
        )
        
        num_questions = st.slider("❓ Number of Questions", 3, 12, 8)
        
        focus_areas = st.multiselect(
            "🎯 Focus Areas",
            ["Leadership", "Teamwork", "Conflict Resolution", "Problem Solving",
             "Communication", "Adaptability", "Initiative", "Time Management",
             "Motivation", "Career Goals"],
            default=["Leadership", "Teamwork", "Problem Solving"],
        )
    
    with col2:
        st.markdown("### 📊 What gets evaluated:")
        competencies = [
            "💬 Communication clarity",
            "🎯 STAR method usage",
            "👥 Leadership & teamwork",
            "🧠 Problem solving approach",
            "💼 Professionalism",
            "🔥 Confidence & tone",
        ]
        for comp in competencies:
            st.markdown(f"• {comp}")
        
        st.markdown("### 💡 Tips:")
        st.markdown("• Use the STAR method (Situation, Task, Action, Result)")
        st.markdown("• Be specific with examples from your experience")
        st.markdown("• Quantify your achievements when possible")
        st.markdown("• Keep answers focused and concise (2-3 minutes per answer)")
    
    if st.button("🚀 Start HR Interview", type="primary", use_container_width=True):
        context = interview_context
        if focus_areas:
            context += f"\nFocus areas: {', '.join(focus_areas)}"
        
        with st.spinner("🤖 Preparing interview questions..."):
            questions = generate_hr_questions(context, num_questions)
        
        if not questions:
            st.error("Failed to generate questions. Please try again.")
            return
        
        st.session_state.hr_session = {
            "questions": questions,
            "answers": [],
            "evaluations": [],
            "current_q": 0,
            "type": "hr",
            "context": interview_context,
        }
        st.session_state.hr_interview_state = "interviewing"
        st.rerun()


def _show_hr_interview(user: dict):
    """Show active HR interview."""
    session = st.session_state.get("hr_session", {})
    
    if not session:
        st.session_state.hr_interview_state = "setup"
        st.rerun()
        return
    
    questions = session["questions"]
    current_q = session["current_q"]
    total_q = len(questions)
    
    if current_q >= total_q:
        _finalize_hr_interview(user, session)
        return
    
    st.progress(current_q / total_q)
    st.markdown(f"**Question {current_q + 1} of {total_q}**")
    
    current_question = questions[current_q]
    question_text = current_question.get("question", "") if isinstance(current_question, dict) else current_question
    q_type = current_question.get("type", "") if isinstance(current_question, dict) else ""
    star_applicable = current_question.get("star_applicable", True) if isinstance(current_question, dict) else True
    
    st.markdown("---")
    st.markdown(f"*{q_type.replace('_', ' ').title()}*")
    st.markdown(f"### 💬 {question_text}")
    
    if star_applicable:
        with st.expander("📋 STAR Method Reminder"):
            st.markdown("""
            **S**ituation — Set the context (where, when, what)  
            **T**ask — Your specific responsibility  
            **A**ction — The exact steps you took  
            **R**esult — The outcome and what you learned  
            """)
    
    answer = st.text_area(
        "✍️ Your Answer",
        height=180,
        placeholder="Share a specific example from your experience... Use the STAR method for behavioral questions.",
        key=f"hr_answer_{current_q}",
    )
    
    eval_criteria = current_question.get("evaluation_criteria", []) if isinstance(current_question, dict) else []
    if eval_criteria:
        with st.expander("🎯 What the interviewer is looking for"):
            for crit in eval_criteria:
                st.markdown(f"• {crit}")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("✅ Submit Answer", type="primary", use_container_width=True):
            if not answer.strip():
                st.warning("Please provide an answer.")
                return
            _process_hr_answer(session, current_question, answer)
    with col2:
        if st.button("⏭️ Skip", use_container_width=True):
            session["answers"].append("(Skipped)")
            session["evaluations"].append({"score": 0})
            session["current_q"] += 1
            st.rerun()
    with col3:
        if st.button("🏁 End", use_container_width=True):
            _finalize_hr_interview(user, session)


def _process_hr_answer(session: dict, question, answer: str):
    """Process HR answer with STAR analysis."""
    question_text = question.get("question", "") if isinstance(question, dict) else question
    
    with st.spinner("🤖 Analyzing your answer..."):
        evaluation = evaluate_hr_answer(question_text, answer)
    
    session["answers"].append(answer)
    session["evaluations"].append(evaluation)
    session["current_q"] += 1
    
    score = evaluation.get("score", 0)
    if score >= 7:
        st.success(f"✅ Strong answer! Score: {score}/10")
    elif score >= 5:
        st.info(f"👍 Good attempt! Score: {score}/10")
    else:
        st.warning(f"⚠️ Needs improvement. Score: {score}/10")
    
    # Show STAR analysis
    star = evaluation.get("star_analysis", {})
    if star:
        cols = st.columns(4)
        for col, (key, label) in zip(cols, [("situation", "S"), ("task", "T"), ("action", "A"), ("result", "R")]):
            part = star.get(key, {})
            present = part.get("present", False)
            with col:
                icon = "✅" if present else "❌"
                st.markdown(f"**{icon} {label}** — {part.get('quality', 'N/A')}")
    
    if evaluation.get("feedback"):
        st.info(evaluation["feedback"])
    
    st.rerun()


def _finalize_hr_interview(user: dict, session: dict):
    """Finalize HR interview."""
    with st.spinner("Generating comprehensive feedback..."):
        score_data = calculate_session_score(session.get("evaluations", []))
        session["score"] = score_data.get("overall", 0)
        
        feedback = generate_session_feedback({
            "questions": session["questions"],
            "answers": session["answers"],
            "evaluations": session["evaluations"],
            "type": "hr",
            "score": session["score"],
        })
        session["feedback_report"] = feedback
    
    save_interview_session(user["id"], {
        "type": "hr",
        "domain": "HR Interview",
        "questions": session["questions"],
        "answers": session["answers"],
        "evaluations": session["evaluations"],
        "score": session["score"],
        "feedback": str(feedback),
    })
    
    st.session_state.hr_interview_state = "results"
    st.rerun()


def _show_hr_results(user: dict):
    """Show HR interview results with competency radar."""
    session = st.session_state.get("hr_session", {})
    feedback = session.get("feedback_report", {})
    evaluations = session.get("evaluations", [])
    
    st.subheader("🏆 HR Interview Complete!")
    
    score = session.get("score", 0)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Final Score", f"{score}%")
    with col2:
        st.metric("📊 Grade", feedback.get("overall_performance", {}).get("grade", "N/A"))
    with col3:
        st.metric("❓ Questions", len(session.get("questions", [])))
    
    # Competency radar chart
    skill_assessment = feedback.get("skill_assessment", {})
    if skill_assessment:
        categories = list(skill_assessment.keys())
        values = list(skill_assessment.values())
        
        fig = go.Figure(go.Scatterpolar(
            r=values,
            theta=[c.replace("_", " ").title() for c in categories],
            fill="toself",
            name="Your Performance",
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="Competency Assessment",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)
    
    col_s, col_i = st.columns(2)
    with col_s:
        st.markdown("### ✅ Key Strengths")
        for s in feedback.get("key_strengths", []):
            st.markdown(f"• {s}")
    with col_i:
        st.markdown("### 📈 Improvements")
        for imp in feedback.get("critical_improvements", []):
            st.markdown(f"• {imp}")
    
    if feedback.get("encouragement"):
        st.success(f"💪 {feedback['encouragement']}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New HR Interview", type="primary", use_container_width=True):
            st.session_state.hr_interview_state = "setup"
            if "hr_session" in st.session_state:
                del st.session_state.hr_session
            st.rerun()
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()