"""
Technical Interview Page - AI-powered technical mock interviews
"""

import streamlit as st
from ai.question_generator import generate_technical_questions, generate_resume_questions
from ai.answer_evaluator import evaluate_answer, calculate_session_score
from ai.followup_generator import generate_followup, should_ask_followup
from ai.feedback_generator import generate_session_feedback
from database.interview_queries import save_interview_session
from config import TECHNICAL_DOMAINS, DIFFICULTY_LEVELS


def show_technical_interview(user: dict):
    """Display the technical interview page."""
    st.title("💻 Technical Interview")
    
    # Check if resume-based questions requested
    use_resume = st.session_state.get("use_resume_questions", False)
    
    if "tech_interview_state" not in st.session_state:
        st.session_state.tech_interview_state = "setup"
    
    state = st.session_state.tech_interview_state
    
    if state == "setup":
        _show_setup(user, use_resume)
    elif state == "interviewing":
        _show_interview(user)
    elif state == "results":
        _show_results(user)


def _show_setup(user: dict, use_resume: bool = False):
    """Show interview setup configuration."""
    st.subheader("⚙️ Configure Your Interview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        interview_source = st.radio(
            "📋 Question Source",
            ["Topic-based", "Resume-based"] if st.session_state.get("resume_data") else ["Topic-based"],
            index=1 if use_resume and st.session_state.get("resume_data") else 0,
        )
        
        if interview_source == "Topic-based":
            domain = st.selectbox(
                "🗂️ Domain",
                list(TECHNICAL_DOMAINS.keys()),
            )
            
            topic = st.selectbox(
                "📌 Topic",
                TECHNICAL_DOMAINS[domain],
            )
        else:
            domain = "Resume-based"
            topic = "Resume"
            st.info("Questions will be generated from your uploaded resume.")
        
        difficulty = st.selectbox("📊 Difficulty Level", DIFFICULTY_LEVELS, index=1)
    
    with col2:
        num_questions = st.slider("❓ Number of Questions", 3, 15, 8)
        
        enable_followup = st.toggle("🔄 Enable Follow-up Questions", value=True)
        
        interview_mode = st.radio(
            "🎭 Interview Mode",
            ["Guided (with hints)", "Real (no hints)"],
        )
        
        st.markdown("### 📋 What to expect:")
        st.markdown(f"• {num_questions} questions on {topic}")
        st.markdown(f"• {difficulty} difficulty level")
        st.markdown(f"• AI evaluation and scoring")
        st.markdown(f"• Detailed feedback at the end")
        if enable_followup:
            st.markdown("• Intelligent follow-up questions")
    
    if st.button("🚀 Start Interview", type="primary", use_container_width=True):
        with st.spinner("🤖 Generating your interview questions..."):
            if interview_source == "Resume-based":
                resume_info = st.session_state.get("resume_data", {}).get("extracted_info", {})
                questions = generate_resume_questions(resume_info, num_questions)
            else:
                questions = generate_technical_questions(domain, topic, difficulty, num_questions)
        
        if not questions:
            st.error("Failed to generate questions. Please try again.")
            return
        
        # Initialize interview session
        st.session_state.tech_session = {
            "questions": questions,
            "answers": [],
            "evaluations": [],
            "current_q": 0,
            "domain": domain,
            "topic": topic,
            "difficulty": difficulty,
            "type": "technical",
            "enable_followup": enable_followup,
            "real_mode": "Real" in interview_mode,
            "followup_queue": [],
            "conversation_history": [],
        }
        st.session_state.tech_interview_state = "interviewing"
        st.session_state.use_resume_questions = False
        st.rerun()


def _show_interview(user: dict):
    """Show the active interview session."""
    session = st.session_state.get("tech_session", {})
    
    if not session:
        st.session_state.tech_interview_state = "setup"
        st.rerun()
        return
    
    questions = session["questions"]
    current_q = session["current_q"]
    total_q = len(questions)
    
    # Handle follow-up questions
    followup_queue = session.get("followup_queue", [])
    
    # Progress
    progress = current_q / total_q
    st.progress(progress)
    st.markdown(f"**Question {min(current_q + 1, total_q)} of {total_q}** | Domain: {session['domain']} | {session['difficulty']}")
    
    if current_q >= total_q and not followup_queue:
        _finalize_interview(user, session)
        return
    
    # Determine current question
    if followup_queue:
        current_question = followup_queue[0]
        is_followup = True
    else:
        current_question = questions[current_q]
        is_followup = False
    
    # Display question
    question_text = current_question.get("question", current_question) if isinstance(current_question, dict) else current_question
    
    st.markdown("---")
    if is_followup:
        st.markdown("🔄 **Follow-up Question:**")
    else:
        q_type = current_question.get("type", "") if isinstance(current_question, dict) else ""
        difficulty = current_question.get("difficulty", "") if isinstance(current_question, dict) else ""
        if q_type or difficulty:
            st.markdown(f"*{q_type} | {difficulty}*")
    
    st.markdown(f"### 🤔 {question_text}")
    
    # Show hints if guided mode
    if not session.get("real_mode") and isinstance(current_question, dict):
        key_points = current_question.get("key_points", current_question.get("expected_topics", []))
        if key_points:
            with st.expander("💡 Hint - Key points to cover"):
                for point in key_points:
                    st.markdown(f"• {point}")
    
    # Answer input
    answer = st.text_area(
        "✍️ Your Answer",
        height=150,
        placeholder="Type your answer here... Be thorough and explain your reasoning.",
        key=f"answer_{current_q}_{len(followup_queue)}",
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("✅ Submit Answer", type="primary", use_container_width=True):
            if not answer.strip():
                st.warning("Please provide an answer before submitting.")
                return
            
            _process_answer(session, current_question, answer, is_followup)
    
    with col2:
        if st.button("⏭️ Skip", use_container_width=True):
            _skip_question(session, is_followup)
    
    with col3:
        if st.button("🏁 End Interview", use_container_width=True):
            _finalize_interview(user, session)
    
    # Show previous answers
    if session.get("answers"):
        with st.expander(f"📚 Previous Answers ({len(session['answers'])})"):
            for i, (q, a, e) in enumerate(zip(
                session["questions"][:len(session["answers"])],
                session["answers"],
                session["evaluations"],
            )):
                q_text = q.get("question", "") if isinstance(q, dict) else q
                score = e.get("score", "?") if isinstance(e, dict) else "?"
                st.markdown(f"**Q{i+1}:** {q_text[:100]}...")
                st.markdown(f"**Score:** {score}/10")
                st.markdown("---")


def _process_answer(session: dict, question, answer: str, is_followup: bool):
    """Process submitted answer."""
    question_text = question.get("question", question) if isinstance(question, dict) else question
    expected_topics = question.get("expected_topics", question.get("key_points", [])) if isinstance(question, dict) else []
    
    with st.spinner("🤖 Evaluating your answer..."):
        evaluation = evaluate_answer(
            question_text, answer, "technical", expected_topics
        )
    
    if not is_followup:
        session["answers"].append(answer)
        session["evaluations"].append(evaluation)
        session["conversation_history"].append({
            "question": question_text,
            "answer": answer,
        })
        
        # Check for follow-up
        if session.get("enable_followup") and should_ask_followup(answer):
            with st.spinner("Generating follow-up..."):
                followup = generate_followup(
                    question_text, answer,
                    session["conversation_history"][-3:],
                    "technical"
                )
            if followup:
                session["followup_queue"] = [{"question": followup, "is_followup": True}]
        
        session["current_q"] += 1
    else:
        # Remove from followup queue
        session["followup_queue"] = session["followup_queue"][1:]
    
    # Show immediate feedback
    score = evaluation.get("score", 0)
    if score >= 7:
        st.success(f"✅ Good answer! Score: {score}/10")
    elif score >= 4:
        st.warning(f"⚠️ Partial answer. Score: {score}/10")
    else:
        st.error(f"❌ Needs improvement. Score: {score}/10")
    
    if evaluation.get("detailed_feedback"):
        st.info(evaluation["detailed_feedback"])
    
    st.rerun()


def _skip_question(session: dict, is_followup: bool):
    """Skip current question."""
    if not is_followup:
        session["answers"].append("(Skipped)")
        session["evaluations"].append({"score": 0, "grade": "Skipped"})
        session["current_q"] += 1
    else:
        session["followup_queue"] = session["followup_queue"][1:]
    st.rerun()


def _finalize_interview(user: dict, session: dict):
    """Finalize and save interview session."""
    
    with st.spinner("📊 Calculating final scores..."):
        score_data = calculate_session_score(session.get("evaluations", []))
        session["score"] = score_data.get("overall", 0)
        
        feedback = generate_session_feedback({
            "questions": session["questions"],
            "answers": session["answers"],
            "evaluations": session["evaluations"],
            "type": "technical",
            "score": session["score"],
        })
        session["feedback_report"] = feedback
    
    # Save to database
    save_interview_session(user["id"], {
        "type": "technical",
        "domain": session.get("domain", ""),
        "difficulty": session.get("difficulty", ""),
        "questions": session.get("questions", []),
        "answers": session.get("answers", []),
        "evaluations": session.get("evaluations", []),
        "score": session["score"],
        "feedback": str(feedback),
    })
    
    st.session_state.tech_interview_state = "results"
    st.rerun()


def _show_results(user: dict):
    """Show interview results."""
    session = st.session_state.get("tech_session", {})
    feedback = session.get("feedback_report", {})
    
    st.subheader("🏆 Interview Complete!")
    
    score = session.get("score", 0)
    grade = feedback.get("overall_performance", {}).get("grade", "N/A")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Final Score", f"{score}%")
    with col2:
        st.metric("📊 Grade", grade)
    with col3:
        st.metric("❓ Questions", len(session.get("questions", [])))
    
    if feedback.get("executive_summary"):
        st.info(f"**Summary:** {feedback['executive_summary']}")
    
    col_s, col_i = st.columns(2)
    with col_s:
        st.markdown("### ✅ Key Strengths")
        for s in feedback.get("key_strengths", []):
            st.markdown(f"• {s}")
    with col_i:
        st.markdown("### 📈 Areas to Improve")
        for i in feedback.get("critical_improvements", []):
            st.markdown(f"• {i}")
    
    # Action plan
    if feedback.get("action_plan"):
        st.markdown("### 📅 Action Plan")
        for phase in feedback["action_plan"]:
            with st.expander(f"📌 {phase.get('week', '')} — {phase.get('focus', '')}"):
                for activity in phase.get("activities", []):
                    st.markdown(f"• {activity}")
    
    if feedback.get("encouragement"):
        st.success(f"💪 {feedback['encouragement']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 New Interview", use_container_width=True, type="primary"):
            st.session_state.tech_interview_state = "setup"
            del st.session_state.tech_session
            st.rerun()
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()
    with col3:
        if st.button("📋 Download Report", use_container_width=True):
            st.session_state.current_page = "reports"
            st.rerun()