"""
Non Technical Interview Page
HR, Marketing, Sales, Business Analyst,
Customer Support, Project Management
"""

import streamlit as st
from datetime import datetime

from ai.question_generator import generate_hr_questions
from ai.answer_evaluator import (
    evaluate_hr_answer,
    calculate_session_score
)

from database.interview_queries import (
    save_interview_session
)


ROLES = [
    "HR",
    "Marketing",
    "Sales",
    "Business Analyst",
    "Customer Support",
    "Project Management",
    "Operations",
    "Finance"
]


def show_non_technical_interview(user: dict):

    st.title("🤝 Non Technical Interview")

    st.markdown(
        """
Practice HR, Behavioral and Role-Specific Interviews
with AI evaluation and feedback.
"""
    )

    initialize_state()

    if not st.session_state.nt_interview_started:
        setup_interview()

    else:
        conduct_interview(user)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

def initialize_state():

    defaults = {

        "nt_interview_started": False,
        "nt_questions": [],
        "nt_current": 0,
        "nt_answers": [],
        "nt_evaluations": [],
        "nt_role": "",
        "nt_start_time": None

    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# --------------------------------------------------
# INTERVIEW SETUP
# --------------------------------------------------

def setup_interview():

    st.subheader("Interview Configuration")

    role = st.selectbox(
        "Select Role",
        ROLES
    )

    num_questions = st.slider(
        "Number of Questions",
        5,
        15,
        10
    )

    if st.button(
        "🚀 Start Interview",
        use_container_width=True
    ):

        with st.spinner(
            "Generating interview questions..."
        ):

            questions = generate_hr_questions(
                context=role,
                num_questions=num_questions
            )

        if not questions:

            st.error(
                "Failed to generate questions."
            )
            return

        st.session_state.nt_questions = questions
        st.session_state.nt_role = role
        st.session_state.nt_interview_started = True
        st.session_state.nt_start_time = datetime.now()

        st.rerun()


# --------------------------------------------------
# INTERVIEW FLOW
# --------------------------------------------------

def conduct_interview(user):

    questions = st.session_state.nt_questions

    current = st.session_state.nt_current

    total = len(questions)

    progress = current / total

    st.progress(progress)

    st.caption(
        f"Question {current + 1} of {total}"
    )

    question = questions[current]

    st.markdown("### Question")

    st.info(
        question.get(
            "question",
            "No question"
        )
    )

    st.markdown(
        f"**Type:** {question.get('type','Behavioral')}"
    )

    answer = st.text_area(
        "Your Answer",
        height=200,
        key=f"answer_{current}"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Submit Answer",
            use_container_width=True
        ):

            if not answer.strip():

                st.warning(
                    "Please enter an answer."
                )
                return

            evaluate_current_answer(
                question,
                answer
            )

            st.rerun()

    with col2:

        if current > 0:

            if st.button(
                "Previous",
                use_container_width=True
            ):

                st.session_state.nt_current -= 1
                st.rerun()

    show_previous_feedback()

    if len(
        st.session_state.nt_answers
    ) == total:

        show_final_report(user)


# --------------------------------------------------
# ANSWER EVALUATION
# --------------------------------------------------

def evaluate_current_answer(
    question,
    answer
):

    evaluation = evaluate_hr_answer(
        question["question"],
        answer
    )

    st.session_state.nt_answers.append(
        answer
    )

    st.session_state.nt_evaluations.append(
        evaluation
    )

    st.session_state.nt_current += 1


# --------------------------------------------------
# SHOW FEEDBACK
# --------------------------------------------------

def show_previous_feedback():

    current = st.session_state.nt_current

    if current == 0:
        return

    evaluation = (
        st.session_state.nt_evaluations[-1]
    )

    st.markdown("---")

    st.subheader("AI Feedback")

    score = evaluation.get(
        "score",
        0
    )

    st.metric(
        "Score",
        f"{score}/10"
    )

    st.success(
        evaluation.get(
            "feedback",
            "Good attempt."
        )
    )

    tips = evaluation.get(
        "improvement_tips",
        []
    )

    if tips:

        st.warning(
            "Areas for Improvement"
        )

        for tip in tips:
            st.write(
                f"• {tip}"
            )


# --------------------------------------------------
# FINAL REPORT
# --------------------------------------------------

def show_final_report(user):

    st.markdown("---")

    st.header(
        "📊 Interview Results"
    )

    summary = calculate_session_score(
        st.session_state.nt_evaluations
    )

    score = summary["overall"]

    st.metric(
        "Overall Score",
        f"{score}%"
    )

    st.metric(
        "Grade",
        summary["grade"]
    )

    evaluations = (
        st.session_state.nt_evaluations
    )

    communication_scores = []

    leadership_scores = []

    teamwork_scores = []

    for ev in evaluations:

        comp = ev.get(
            "competencies",
            {}
        )

        communication_scores.append(
            comp.get(
                "communication",
                0
            )
        )

        leadership_scores.append(
            comp.get(
                "leadership",
                0
            )
        )

        teamwork_scores.append(
            comp.get(
                "teamwork",
                0
            )
        )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Communication",
            round(
                sum(
                    communication_scores
                ) /
                max(
                    len(
                        communication_scores
                    ),
                    1
                ),
                1
            )
        )

    with col2:

        st.metric(
            "Leadership",
            round(
                sum(
                    leadership_scores
                ) /
                max(
                    len(
                        leadership_scores
                    ),
                    1
                ),
                1
            )
        )

    with col3:

        st.metric(
            "Teamwork",
            round(
                sum(
                    teamwork_scores
                ) /
                max(
                    len(
                        teamwork_scores
                    ),
                    1
                ),
                1
            )
        )

    duration = (
        datetime.now()
        - st.session_state.nt_start_time
    )

    session_data = {

        "type":
            "non_technical",

        "domain":
            st.session_state.nt_role,

        "difficulty":
            "Medium",

        "questions":
            st.session_state.nt_questions,

        "answers":
            st.session_state.nt_answers,

        "evaluations":
            st.session_state.nt_evaluations,

        "score":
            score,

        "feedback":
            summary["grade"],

        "duration":
            int(
                duration.total_seconds()
                / 60
            )

    }

    if st.button(
        "💾 Save Results",
        use_container_width=True
    ):

        session_id = (
            save_interview_session(
                user["id"],
                session_data
            )
        )

        if session_id:

            st.success(
                "Interview saved successfully."
            )

        else:

            st.error(
                "Failed to save interview."
            )

    if st.button(
        "🔄 Start New Interview",
        use_container_width=True
    ):

        reset_interview()

        st.rerun()


# --------------------------------------------------
# RESET
# --------------------------------------------------

def reset_interview():

    keys = [

        "nt_interview_started",
        "nt_questions",
        "nt_current",
        "nt_answers",
        "nt_evaluations",
        "nt_role",
        "nt_start_time"

    ]

    for key in keys:

        if key in st.session_state:
            del st.session_state[key]