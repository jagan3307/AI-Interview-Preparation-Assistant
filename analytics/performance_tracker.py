"""
Performance Tracker
Tracks interview progress, scores, strengths and weaknesses
"""

from database.interview_queries import (
    get_interview_sessions
)


class PerformanceTracker:

    def __init__(self, user_id):

        self.user_id = user_id

        self.sessions = get_interview_sessions(
            user_id,
            limit=500
        )

    # ------------------------------------
    # OVERALL METRICS
    # ------------------------------------

    def get_summary(self):

        if not self.sessions:

            return {

                "total_interviews": 0,
                "average_score": 0,
                "best_score": 0,
                "latest_score": 0

            }

        scores = [

            session.get(
                "score",
                0
            )

            for session in self.sessions

        ]

        return {

            "total_interviews":
                len(self.sessions),

            "average_score":
                round(
                    sum(scores) /
                    len(scores),
                    2
                ),

            "best_score":
                max(scores),

            "latest_score":
                scores[0]

        }

    # ------------------------------------
    # SCORE TREND
    # ------------------------------------

    def get_score_trend(self):

        trend = []

        for session in reversed(
            self.sessions
        ):

            trend.append({

                "date":
                    session.get(
                        "created_at",
                        ""
                    )[:10],

                "score":
                    session.get(
                        "score",
                        0
                    )

            })

        return trend

    # ------------------------------------
    # INTERVIEW TYPE PERFORMANCE
    # ------------------------------------

    def get_type_performance(self):

        result = {}

        for session in self.sessions:

            interview_type = session.get(
                "interview_type",
                "Unknown"
            )

            result.setdefault(
                interview_type,
                []
            )

            result[
                interview_type
            ].append(

                session.get(
                    "score",
                    0
                )

            )

        output = {}

        for key, values in result.items():

            output[key] = round(

                sum(values) /
                len(values),

                2

            )

        return output

    # ------------------------------------
    # STRENGTHS
    # ------------------------------------

    def get_strengths(self):

        strengths = []

        for session in self.sessions:

            evaluations = session.get(
                "evaluations",
                []
            )

            for ev in evaluations:

                strengths.extend(

                    ev.get(
                        "strengths",
                        []
                    )

                )

        return strengths[:20]

    # ------------------------------------
    # IMPROVEMENTS
    # ------------------------------------

    def get_improvements(self):

        improvements = []

        for session in self.sessions:

            evaluations = session.get(
                "evaluations",
                []
            )

            for ev in evaluations:

                improvements.extend(

                    ev.get(
                        "improvements",
                        []
                    )

                )

        return improvements[:20]