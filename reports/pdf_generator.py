"""
PDF Report Generator
Generates Interview, ATS and Analytics Reports
"""

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from reportlab.lib import colors

from datetime import datetime


class PDFGenerator:

    def __init__(self):

        self.styles = getSampleStyleSheet()

    # --------------------------------------
    # INTERVIEW REPORT
    # --------------------------------------

    def generate_interview_report(

        self,
        output_path,
        user_name,
        session

    ):

        doc = SimpleDocTemplate(
            output_path
        )

        elements = []

        title = Paragraph(

            "AI Interview Report",

            self.styles["Title"]

        )

        elements.append(title)

        elements.append(
            Spacer(1, 20)
        )

        info = f"""
        Candidate: {user_name}<br/>
        Interview Type:
        {session.get('interview_type','')}<br/>
        Domain:
        {session.get('domain','')}<br/>
        Score:
        {session.get('score',0)}%<br/>
        Date:
        {session.get('created_at','')}
        """

        elements.append(

            Paragraph(
                info,
                self.styles["BodyText"]
            )

        )

        elements.append(
            Spacer(1, 20)
        )

        questions = session.get(
            "questions",
            []
        )

        answers = session.get(
            "answers",
            []
        )

        evaluations = session.get(
            "evaluations",
            []
        )

        for i in range(

            min(
                len(questions),
                len(answers)
            )

        ):

            q = questions[i]

            question_text = (

                q.get("question","")

                if isinstance(
                    q,
                    dict
                )

                else str(q)

            )

            elements.append(

                Paragraph(

                    f"<b>Question {i+1}</b>",

                    self.styles["Heading2"]

                )

            )

            elements.append(

                Paragraph(

                    question_text,

                    self.styles["BodyText"]

                )

            )

            elements.append(

                Paragraph(

                    f"<b>Answer:</b><br/>{answers[i]}",

                    self.styles["BodyText"]

                )

            )

            if i < len(evaluations):

                elements.append(

                    Paragraph(

                        f"<b>Feedback:</b><br/>{evaluations[i].get('detailed_feedback','')}",

                        self.styles["BodyText"]

                    )

                )

            elements.append(
                Spacer(1, 10)
            )

        doc.build(elements)

        return output_path

    # --------------------------------------
    # ATS REPORT
    # --------------------------------------

    def generate_ats_report(

        self,
        output_path,
        user_name,
        resume_data

    ):

        doc = SimpleDocTemplate(
            output_path
        )

        elements = []

        elements.append(

            Paragraph(

                "ATS Resume Report",

                self.styles["Title"]

            )

        )

        elements.append(
            Spacer(1, 20)
        )

        ats_score = resume_data.get(
            "ats_score",
            0
        )

        elements.append(

            Paragraph(

                f"Candidate: {user_name}",

                self.styles["BodyText"]

            )

        )

        elements.append(

            Paragraph(

                f"ATS Score: {ats_score}%",

                self.styles["BodyText"]

            )

        )

        elements.append(
            Spacer(1, 20)
        )

        feedback = resume_data.get(
            "feedback",
            ""
        )

        elements.append(

            Paragraph(

                feedback,

                self.styles["BodyText"]

            )

        )

        doc.build(elements)

        return output_path

    # --------------------------------------
    # PERFORMANCE REPORT
    # --------------------------------------

    def generate_performance_report(

        self,
        output_path,
        user_name,
        sessions

    ):

        doc = SimpleDocTemplate(
            output_path
        )

        elements = []

        elements.append(

            Paragraph(

                "Performance Analytics Report",

                self.styles["Title"]

            )

        )

        elements.append(
            Spacer(1, 20)
        )

        total = len(sessions)

        scores = [

            s.get(
                "score",
                0
            )

            for s in sessions

        ]

        avg_score = (

            round(
                sum(scores) /
                len(scores),
                2
            )

            if scores

            else 0

        )

        best_score = (

            max(scores)

            if scores

            else 0

        )

        summary = f"""
        Candidate: {user_name}<br/>
        Total Interviews: {total}<br/>
        Average Score: {avg_score}%<br/>
        Best Score: {best_score}%<br/>
        Generated On:
        {datetime.now()}
        """

        elements.append(

            Paragraph(

                summary,

                self.styles["BodyText"]

            )

        )

        elements.append(
            PageBreak()
        )

        for idx, session in enumerate(
            sessions,
            start=1
        ):

            text = f"""
            Interview #{idx}<br/>
            Type:
            {session.get('interview_type','')}<br/>
            Score:
            {session.get('score',0)}%
            """

            elements.append(

                Paragraph(

                    text,

                    self.styles["BodyText"]

                )

            )

            elements.append(
                Spacer(1, 10)
            )

        doc.build(elements)

        return output_path