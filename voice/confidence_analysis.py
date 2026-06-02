
# voice/confidence_analysis.py

"""
Voice Confidence Analysis
"""

import re


class ConfidenceAnalyzer:

    FILLER_WORDS = [

        "um",
        "uh",
        "like",
        "actually",
        "basically",
        "you know"

    ]

    def analyze(
        self,
        transcript: str
    ):

        words = transcript.split()

        total_words = len(words)

        filler_count = 0

        for word in words:

            if word.lower() in self.FILLER_WORDS:

                filler_count += 1

        filler_ratio = (

            filler_count /
            total_words

            if total_words

            else 0

        )

        confidence_score = max(

            0,

            100 -
            int(filler_ratio * 100)

        )

        return {

            "confidence_score":
                confidence_score,

            "filler_words":
                filler_count,

            "total_words":
                total_words

        }

