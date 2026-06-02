# pages/voice_interview.py

"""
Voice Interview Page
Speech → Text → AI Evaluation
"""

import streamlit as st
from datetime import datetime

from voice.speech_to_text import SpeechToText
from voice.confidence_analysis import ConfidenceAnalyzer
from voice.communication_analysis import CommunicationAnalyzer

from ai.question_generator import (
    generate_technical_questions,
    generate_hr_questions
)

from ai.answer_evaluator import (
    evaluate_answer,
    evaluate_hr_answer,
    calculate_session_score
)

from database.interview_queries import (
    save_interview_session
)


def show_voice_interview(user):

    st.title("🎙️ AI Voice Interview")

    initialize_state()

    if not st.session_state.voice_started:

        setup_voice_interview()

    else:

        conduct_voice_interview(user)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

def initialize_state():

    defaults = {

        "voice_started": False,
        "voice_questions": [],
        "voice_answers": [],
        "voice_evaluations": [],
        "voice_current": 0,
        "voice_type": "",
        "voice_start_time": None

    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


# --------------------------------------------------
# SETUP
# --------------------------------------------------

def setup_voice_interview():

    st.subheader(
        "Interview Configuration"
    )

    interview_type = st.selectbox(

        "Interview Type",

        [
            "Technical",
            "HR"
        ]

    )

    difficulty = st.selectbox(

        "Difficulty",

        [
            "Easy",
            "Medium",
            "Hard"
        ]

    )

    topic = st.text_input(
        "Topic / Domain",
        "Python"
    )

    total_questions = st.slider(
        "Questions",
        3,
        15,
        5
    )

    if st.button(
        "🚀 Start Voice Interview",
        use_container_width=True
    ):

        with st.spinner(
            "Generating Questions..."
        ):

            if interview_type == "Technical":

                questions = generate_technical_questions(

                    domain=topic,

                    topic=topic,

                    difficulty=difficulty,

                    num_questions=total_questions

                )

            else:

                questions = generate_hr_questions(

                    context=topic,

                    num_questions=total_questions

                )

        if not questions:

            st.error(
                "Question generation failed."
            )
            return

        st.session_state.voice_questions = questions
        st.session_state.voice_started = True
        st.session_state.voice_type = interview_type
        st.session_state.voice_start_time = datetime.now()

        st.rerun()


# --------------------------------------------------
# INTERVIEW FLOW
# --------------------------------------------------

def conduct_voice_interview(user):

    questions = st.session_state.voice_questions

    current = st.session_state.voice_current

    total = len(questions)

    if current >= total:

        show_final_report(user)
        return

    progress = current / total

    st.progress(progress)

    st.markdown(
        f"### Question {current+1}/{total}"
    )

    question = questions[current]

    st.info(
        question.get(
            "question",
            "No Question"
        )
    )

    st.markdown("---")

    st.subheader(
        "Upload Voice Answer"
    )

    audio_file = st.file_uploader(

        "Upload WAV Audio",

        type=[
            "wav"
        ],

        key=f"audio_{current}"

    )

    if audio_file:

        transcriber = SpeechToText()

        with st.spinner(
            "Converting Speech To Text..."
        ):

            result = transcriber.transcribe_file(
                audio_file
            )

        if result["success"]:

            transcript = result["text"]

            st.success(
                "Speech Converted"
            )

            st.text_area(

                "Transcript",

                transcript,

                height=200

            )

            if st.button(
                "Evaluate Answer",
                use_container_width=True
            ):

                evaluate_voice_answer(
                    question,
                    transcript
                )

                st.rerun()

        else:

            st.error(
                result["error"]
            )


# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

def evaluate_voice_answer(

    question,
    transcript

):

    confidence = ConfidenceAnalyzer()

    communication = CommunicationAnalyzer()

    confidence_result = confidence.analyze(
        transcript
    )

    communication_result = communication.analyze(
        transcript
    )

    if st.session_state.voice_type == "HR":

        evaluation = evaluate_hr_answer(

            question["question"],
            transcript

        )

    else:

        evaluation = evaluate_answer(

            question["question"],
            transcript,

            interview_type="technical"

        )

    evaluation["confidence_score"] = (

        confidence_result[
            "confidence_score"
        ]

    )

    evaluation["communication_score"] = (

        communication_result[
            "communication_score"
        ]

    )

    st.session_state.voice_answers.append(
        transcript
    )

    st.session_state.voice_evaluations.append(
        evaluation
    )

    st.session_state.voice_current += 1


# --------------------------------------------------
# FINAL REPORT
# --------------------------------------------------

def show_final_report(user):

    st.header(
        "📊 Voice Interview Results"
    )

    evaluations = (
        st.session_state.voice_evaluations
    )

    result = calculate_session_score(
        evaluations
    )

    st.metric(
        "Overall Score",
        f"{result['overall']}%"
    )

    st.metric(
        "Grade",
        result["grade"]
    )

    confidence_scores = [

        e.get(
            "confidence_score",
            0
        )

        for e in evaluations

    ]

    communication_scores = [

        e.get(
            "communication_score",
            0
        )

        for e in evaluations

    ]

    col1, col2 = st.columns(2)

    with col1:

        st.metric(

            "Confidence",

            round(
                sum(confidence_scores)
                /
                max(
                    len(confidence_scores),
                    1
                ),
                1
            )

        )

    with col2:

        st.metric(

            "Communication",

            round(
                sum(
                    communication_scores
                )
                /
                max(
                    len(
                        communication_scores
                    ),
                    1
                ),
                1
            )

        )

    st.markdown("---")

    for idx, ev in enumerate(
        evaluations,
        start=1
    ):

        with st.expander(
            f"Question {idx}"
        ):

            st.write(
                ev.get(
                    "detailed_feedback",
                    "No feedback"
                )
            )

            st.metric(
                "Score",
                ev.get(
                    "score",
                    0
                )
            )

    if st.button(
        "💾 Save Interview",
        use_container_width=True
    ):

        save_voice_session(user)

    if st.button(
        "🔄 New Voice Interview",
        use_container_width=True
    ):

        reset_voice_interview()

        st.rerun()


# --------------------------------------------------
# SAVE
# --------------------------------------------------

def save_voice_session(user):

    duration = (

        datetime.now()

        -

        st.session_state.voice_start_time

    )

    session_data = {

        "type":
            "voice_interview",

        "domain":
            st.session_state.voice_type,

        "difficulty":
            "Medium",

        "questions":
            st.session_state.voice_questions,

        "answers":
            st.session_state.voice_answers,

        "evaluations":
            st.session_state.voice_evaluations,

        "score":

            calculate_session_score(
                st.session_state.voice_evaluations
            )["overall"],

        "feedback":
            "Voice Interview",

        "duration":
            int(
                duration.total_seconds()
                / 60
            )

    }

    session_id = save_interview_session(

        user["id"],
        session_data

    )

    if session_id:

        st.success(
            "Interview Saved Successfully"
        )

    else:

        st.error(
            "Save Failed"
        )


# --------------------------------------------------
# RESET
# --------------------------------------------------

def reset_voice_interview():

    keys = [

        "voice_started",
        "voice_questions",
        "voice_answers",
        "voice_evaluations",
        "voice_current",
        "voice_type",
        "voice_start_time"

    ]

    for key in keys:

        if key in st.session_state:

            del st.session_state[key]

