"""
Common Helper Functions
"""

from datetime import datetime
import uuid


def generate_id():

    return str(
        uuid.uuid4()
    )


def current_timestamp():

    return datetime.utcnow().isoformat()


def format_date(date_string):

    try:

        date = datetime.fromisoformat(
            date_string.replace(
                "Z",
                ""
            )
        )

        return date.strftime(
            "%d %b %Y"
        )

    except Exception:

        return date_string


def percentage(part, whole):

    if whole == 0:
        return 0

    return round(
        (part / whole) * 100,
        2
    )


def safe_int(value):

    try:
        return int(value)
    except:
        return 0


def safe_float(value):

    try:
        return float(value)
    except:
        return 0.0


def truncate_text(
    text,
    length=150
):

    if not text:
        return ""

    if len(text) <= length:
        return text

    return text[:length] + "..."