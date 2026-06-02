"""
Aptitude Test Page
Quantitative Aptitude
Logical Reasoning
Verbal Ability
"""

import streamlit as st
from datetime import datetime

from ai.question_generator import (
    generate_aptitude_questions
)

from database.interview_queries import (
    save_aptitude_result
)


CATEGORIES = {

    "Quantitative Aptitude": [

        "Percentages",
        "Profit and Loss",
        "Probability",
        "Time and Work",
        "Time Speed Distance",
        "Simple Interest",
        "Compound Interest"

    ],

    "Logical Reasoning": [

        "Blood Relations",
        "Seating Arrangement",
        "Puzzles",
        "Coding Decoding",
        "Series"

    ],

    "Verbal Ability": [

        "Grammar",
        "Vocabulary",
        "Reading Comprehension",
        "Sentence Correction"

    ]
}


def show_aptitude_test(user: dict):

    st.title("🧮 Aptitude Assessment")

    initialize_state()

    if not st.session_state.aptitude_started:
        setup_test()

    else:
        conduct_test(user)


# ------------------------------------------------
# SESSION STATE
# ------------------------------------------------

def initialize_state():

    defaults = {

        "aptitude_started": False,
        "aptitude_questions": [],
        "aptitude_answers": {},
        "aptitude_category": "",
        "aptitude_subcategory": "",
        "aptitude_start_time": None,
        "aptitude_submitted": False

    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# ------------------------------------------------
# SETUP
# ------------------------------------------------

def setup_test():

    st.subheader("Configure Aptitude Test")

    category = st.selectbox(
        "Category",
        list(CATEGORIES.keys())
    )

    subcategory = st.selectbox(
        "Topic",
        CATEGORIES[category]
    )

    num_questions = st.slider(
        "Number of Questions",
        5,
        20,
        10
    )

    if st.button(
        "🚀 Start Test",
        use_container_width=True
    ):

        with st.spinner(
            "Generating aptitude questions..."
        ):

            questions = generate_aptitude_questions(
                category,
                subcategory,
                num_questions
            )

        if not questions:

            st.error(
                "Failed to generate questions."
            )
            return

        st.session_state.aptitude_questions = questions
        st.session_state.aptitude_category = category
        st.session_state.aptitude_subcategory = subcategory
        st.session_state.aptitude_started = True
        st.session_state.aptitude_start_time = datetime.now()

        st.rerun()


# ------------------------------------------------
# TEST SCREEN
# ------------------------------------------------

def conduct_test(user):

    st.subheader(
        f"{st.session_state.aptitude_category}"
    )

    questions = (
        st.session_state.aptitude_questions
    )

    total = len(questions)

    for idx, question in enumerate(
        questions
    ):

        st.markdown("---")

        st.markdown(
            f"### Question {idx+1}"
        )

        st.write(
            question.get(
                "question",
                ""
            )
        )

        options = question.get(
            "options",
            []
        )

        selected = st.radio(

            "Choose your answer",

            options,

            key=f"q_{idx}"

        )

        st.session_state.aptitude_answers[
            idx
        ] = selected

    st.markdown("---")

    if st.button(
        "✅ Submit Test",
        use_container_width=True
    ):

        st.session_state.aptitude_submitted = True

    if st.session_state.aptitude_submitted:

        show_results(user)


# ------------------------------------------------
# RESULTS
# ------------------------------------------------

def show_results(user):

    st.header("📊 Test Results")

    questions = (
        st.session_state.aptitude_questions
    )

    answers = (
        st.session_state.aptitude_answers
    )

    correct = 0

    detailed_results = []

    for idx, question in enumerate(
        questions
    ):

        user_answer = answers.get(
            idx,
            ""
        )

        correct_answer = question.get(
            "correct_answer",
            ""
        )

        selected_letter = (
            user_answer[:1]
            if user_answer
            else ""
        )

        is_correct = (
            selected_letter ==
            correct_answer
        )

        if is_correct:
            correct += 1

        detailed_results.append({

            "question":
                question.get(
                    "question"
                ),

            "selected":
                user_answer,

            "correct":
                correct_answer,

            "explanation":
                question.get(
                    "explanation",
                    ""
                ),

            "status":
                is_correct

        })

    total = len(questions)

    percentage = round(
        (correct / total) * 100,
        2
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Correct",
            correct
        )

    with col2:

        st.metric(
            "Total",
            total
        )

    with col3:

        st.metric(
            "Score",
            f"{percentage}%"
        )

    st.markdown("---")

    if percentage >= 80:

        st.success(
            "Excellent Performance 🎉"
        )

    elif percentage >= 60:

        st.info(
            "Good Performance 👍"
        )

    else:

        st.warning(
            "Needs Improvement 📚"
        )

    st.subheader(
        "Detailed Analysis"
    )

    for i, result in enumerate(
        detailed_results
    ):

        with st.expander(
            f"Question {i+1}"
        ):

            st.write(
                result["question"]
            )

            if result["status"]:

                st.success(
                    f"Correct: {result['selected']}"
                )

            else:

                st.error(
                    f"Your Answer: {result['selected']}"
                )

                st.info(
                    f"Correct Answer: {result['correct']}"
                )

            st.write(
                result["explanation"]
            )

    save_results(
        user,
        correct,
        total,
        percentage
    )


# ------------------------------------------------
# SAVE RESULTS
# ------------------------------------------------

def save_results(

    user,
    correct,
    total,
    percentage

):

    duration = (

        datetime.now()
        -
        st.session_state.aptitude_start_time

    )

    data = {

        "category":
            st.session_state.aptitude_category,

        "score":
            percentage,

        "total":
            total,

        "correct":
            correct,

        "time_taken":
            int(
                duration.total_seconds()
            )

    }

    if "aptitude_saved" not in st.session_state:

        success = save_aptitude_result(

            user["id"],
            data

        )

        if success:

            st.session_state.aptitude_saved = True

            st.success(
                "Result Saved Successfully"
            )


# ------------------------------------------------
# RESET
# ------------------------------------------------

def reset_test():

    keys = [

        "aptitude_started",
        "aptitude_questions",
        "aptitude_answers",
        "aptitude_category",
        "aptitude_subcategory",
        "aptitude_start_time",
        "aptitude_submitted",
        "aptitude_saved"

    ]

    for key in keys:

        if key in st.session_state:
            del st.session_state[key]

