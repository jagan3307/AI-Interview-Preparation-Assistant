"""
Validation Utilities
"""

import re


def validate_email(email):

    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    return bool(
        re.match(
            pattern,
            email
        )
    )


def validate_password(password):

    if len(password) < 6:

        return False, (
            "Password must contain "
            "at least 6 characters."
        )

    return True, "Valid"


def validate_name(name):

    return len(
        name.strip()
    ) >= 2


def validate_phone(phone):

    pattern = r'^\d{10}$'

    return bool(
        re.match(
            pattern,
            phone
        )
    )


def validate_resume_file(filename):

    allowed = [

        ".pdf",
        ".docx"

    ]

    return any(

        filename.lower().endswith(
            ext
        )

        for ext in allowed

    )


def validate_score(score):

    return 0 <= score <= 100