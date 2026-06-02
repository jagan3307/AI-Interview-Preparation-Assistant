
# voice/communication_analysis.py

"""
Communication Skill Analysis
"""

import re


class CommunicationAnalyzer:

    def analyze(
        self,
        transcript
    ):

        sentences = re.split(

            r"[.!?]",

            transcript

        )

        words = transcript.split()

        sentence_count = max(
            len(sentences),
            1
        )

        avg_length = (

            len(words) /
            sentence_count

        )

        clarity_score = min(

            int(avg_length * 4),

            100

        )

        grammar_score = min(

            int(len(words) * 0.5),

            100

        )

        communication_score = (

            clarity_score +
            grammar_score

        ) / 2

        return {

            "clarity_score":
                round(
                    clarity_score,
                    2
                ),

            "grammar_score":
                round(
                    grammar_score,
                    2
                ),

            "communication_score":
                round(
                    communication_score,
                    2
                )

        }

