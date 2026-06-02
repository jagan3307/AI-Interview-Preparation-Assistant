"""
Interview Readiness Calculator
"""

from database.interview_queries import (
    get_interview_sessions
)

from database.resume_queries import (
    get_latest_resume
)


class ReadinessScore:

    def __init__(self, user_id):

        self.user_id = user_id

    def calculate(self):

        sessions = get_interview_sessions(
            self.user_id,
            limit=50
        )

        resume = get_latest_resume(
            self.user_id
        )

        interview_score = 0

        if sessions:

            interview_score = sum(

                s.get(
                    "score",
                    0
                )

                for s in sessions

            ) / len(sessions)

        ats_score = 0

        if resume:

            ats_score = resume.get(
                "ats_score",
                0
            )

        practice_score = min(

            len(sessions) * 5,

            100

        )

        readiness = (

            interview_score * 0.5

            +

            ats_score * 0.3

            +

            practice_score * 0.2

        )

        readiness = round(
            readiness,
            2
        )

        return {

            "readiness_score":
                readiness,

            "interview_score":
                interview_score,

            "ats_score":
                ats_score,

            "practice_score":
                practice_score

        }

    def get_level(self, score):

        if score >= 85:
            return "Interview Ready 🚀"

        elif score >= 70:
            return "Almost Ready 👍"

        elif score >= 50:
            return "Need More Practice 📚"

        return "Beginner 🎯"