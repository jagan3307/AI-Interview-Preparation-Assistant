"""
Coding Interview Page - Code editor with AI evaluation
"""

import streamlit as st
from ai.question_generator import generate_coding_question
from ai.answer_evaluator import evaluate_code
from database.interview_queries import save_interview_session
import time


CODING_TOPICS = [
    "Arrays", "Strings", "Linked Lists", "Trees", "Graphs",
    "Dynamic Programming", "Sorting", "Searching", "Recursion",
    "Stack & Queue", "Hash Tables", "Binary Search", "Two Pointers",
    "Sliding Window", "Backtracking", "Greedy",
]

LANGUAGE_TEMPLATES = {
    "Python": "def solution():\n    # Your code here\n    pass\n",
    "Java": "public class Solution {\n    public static void main(String[] args) {\n        // Your code here\n    }\n}\n",
    "C++": "#include <iostream>\nusing namespace std;\n\nint main() {\n    // Your code here\n    return 0;\n}\n",
    "JavaScript": "function solution() {\n    // Your code here\n}\n",
}


def show_coding_interview(user: dict):
    """Display the coding interview page."""
    st.title("🖥️ Coding Interview")
    st.markdown("Practice coding problems with AI-powered evaluation.")
    
    if "coding_state" not in st.session_state:
        st.session_state.coding_state = "setup"
    
    state = st.session_state.coding_state
    
    if state == "setup":
        _show_coding_setup()
    elif state == "coding":
        _show_coding_problem(user)
    elif state == "results":
        _show_coding_results(user)


def _show_coding_setup():
    """Show coding problem setup."""
    st.subheader("⚙️ Configure Coding Problem")
    
    col1, col2 = st.columns(2)
    
    with col1:
        difficulty = st.selectbox("📊 Difficulty", ["Easy", "Medium", "Hard"])
        topic = st.selectbox("📌 Topic", CODING_TOPICS)
        language = st.selectbox("💻 Programming Language", list(LANGUAGE_TEMPLATES.keys()))
    
    with col2:
        st.markdown("### 🎯 What to expect:")
        st.markdown("• One coding problem with examples")
        st.markdown("• Built-in code editor")
        st.markdown("• Test case validation")
        st.markdown("• AI evaluation of your solution")
        st.markdown("• Time & space complexity analysis")
        st.markdown("• Code quality feedback")
        
        show_hints = st.toggle("💡 Show hints if stuck", value=True)
    
    if st.button("🚀 Get Coding Problem", type="primary", use_container_width=True):
        with st.spinner("🤖 Generating coding problem..."):
            problem = generate_coding_question(difficulty, topic)
        
        if not problem:
            st.error("Failed to generate problem. Please try again.")
            return
        
        st.session_state.coding_session = {
            "problem": problem,
            "language": language,
            "code": LANGUAGE_TEMPLATES.get(language, ""),
            "start_time": time.time(),
            "show_hints": show_hints,
            "hints_used": 0,
            "submitted": False,
        }
        st.session_state.coding_state = "coding"
        st.rerun()


def _show_coding_problem(user: dict):
    """Show the coding problem and editor."""
    session = st.session_state.get("coding_session", {})
    problem = session.get("problem", {})
    
    if not problem:
        st.session_state.coding_state = "setup"
        st.rerun()
        return
    
    # Timer
    elapsed = time.time() - session.get("start_time", time.time())
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    col_title, col_timer = st.columns([3, 1])
    with col_title:
        difficulty = problem.get("difficulty", "Medium")
        color = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(difficulty, "⚪")
        st.markdown(f"### {color} {problem.get('title', 'Coding Problem')} — {difficulty}")
    with col_timer:
        st.metric("⏱️ Time", f"{minutes:02d}:{seconds:02d}")
    
    col_problem, col_editor = st.columns([1, 1])
    
    with col_problem:
        st.markdown("#### 📋 Problem Description")
        st.markdown(problem.get("description", ""))
        
        st.markdown("#### 📝 Examples")
        for i, example in enumerate(problem.get("examples", []), 1):
            with st.expander(f"Example {i}"):
                st.code(f"Input: {example.get('input', '')}\nOutput: {example.get('output', '')}")
                if example.get("explanation"):
                    st.markdown(f"**Explanation:** {example['explanation']}")
        
        st.markdown("#### ⚠️ Constraints")
        for constraint in problem.get("constraints", []):
            st.markdown(f"• {constraint}")
        
        if session.get("show_hints") and problem.get("hints"):
            if st.button(f"💡 Get Hint ({session.get('hints_used', 0)}/{len(problem['hints'])} used)"):
                hints_used = session.get("hints_used", 0)
                if hints_used < len(problem["hints"]):
                    st.info(problem["hints"][hints_used])
                    session["hints_used"] = hints_used + 1
    
    with col_editor:
        st.markdown(f"#### 💻 Code Editor ({session.get('language', 'Python')})")
        
        code = st.text_area(
            "Write your solution:",
            value=session.get("code", ""),
            height=400,
            key="code_editor",
            help="Write your complete solution here",
        )
        session["code"] = code
        
        st.markdown("#### 🧪 Test Cases")
        test_cases = problem.get("test_cases", [])
        if test_cases:
            for i, tc in enumerate(test_cases[:3]):
                st.markdown(f"**Test {i+1}:** Input: `{tc.get('input', '')}` → Expected: `{tc.get('expected', '')}`")
        
        col_submit, col_reset = st.columns(2)
        with col_submit:
            if st.button("✅ Submit Solution", type="primary", use_container_width=True):
                if not code.strip() or code == LANGUAGE_TEMPLATES.get(session.get("language", "Python"), ""):
                    st.warning("Please write your solution before submitting.")
                else:
                    session["submitted_code"] = code
                    session["time_taken"] = elapsed
                    _evaluate_and_finalize(user, session, problem)
        
        with col_reset:
            if st.button("🔄 Reset Code", use_container_width=True):
                session["code"] = LANGUAGE_TEMPLATES.get(session.get("language", "Python"), "")
                st.rerun()
    
    if st.button("❌ Quit Problem", use_container_width=True):
        st.session_state.coding_state = "setup"
        if "coding_session" in st.session_state:
            del st.session_state.coding_session
        st.rerun()


def _evaluate_and_finalize(user: dict, session: dict, problem: dict):
    """Evaluate submitted code and show results."""
    with st.spinner("🤖 Evaluating your solution..."):
        evaluation = evaluate_code(session.get("submitted_code", ""), problem)
    
    session["evaluation"] = evaluation
    
    # Save to database
    save_interview_session(user["id"], {
        "type": "coding",
        "domain": "Coding",
        "difficulty": problem.get("difficulty", "Medium"),
        "questions": [problem],
        "answers": [session.get("submitted_code", "")],
        "evaluations": [evaluation],
        "score": evaluation.get("overall_score", 0) * 10,
        "feedback": evaluation.get("feedback", ""),
    })
    
    st.session_state.coding_state = "results"
    st.rerun()


def _show_coding_results(user: dict):
    """Show coding evaluation results."""
    session = st.session_state.get("coding_session", {})
    evaluation = session.get("evaluation", {})
    problem = session.get("problem", {})
    
    st.subheader("📊 Solution Evaluation")
    
    # Score metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Overall", f"{evaluation.get('overall_score', 0)}/10")
    with col2:
        st.metric("🎯 Correctness", f"{evaluation.get('correctness', 0)}/10")
    with col3:
        tc = evaluation.get("time_complexity", {})
        st.metric("⏱️ Time Complexity", tc.get("actual", "N/A"))
    with col4:
        sc = evaluation.get("space_complexity", {})
        st.metric("💾 Space Complexity", sc.get("actual", "N/A"))
    
    # Code quality
    st.markdown("### 📋 Code Quality")
    st.metric("Code Quality Score", f"{evaluation.get('code_quality', 0)}/10")
    
    # Feedback
    if evaluation.get("feedback"):
        st.info(evaluation["feedback"])
    
    col_good, col_issues = st.columns(2)
    with col_good:
        st.markdown("### ✅ Good Practices")
        for g in evaluation.get("good_practices", []):
            st.markdown(f"• {g}")
    with col_issues:
        st.markdown("### ⚠️ Issues Found")
        for issue in evaluation.get("issues", []):
            st.markdown(f"• {issue}")
    
    st.markdown("### 💡 Improvements")
    for imp in evaluation.get("improvements", []):
        st.markdown(f"• {imp}")
    
    # Show submitted code
    with st.expander("📄 Your Submitted Code"):
        st.code(session.get("submitted_code", ""), language=session.get("language", "python").lower())
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Try Another Problem", type="primary", use_container_width=True):
            st.session_state.coding_state = "setup"
            if "coding_session" in st.session_state:
                del st.session_state.coding_session
            st.rerun()
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()