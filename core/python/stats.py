from sqlalchemy import text

from configuration import engine
from models import ChatSession, Feedback

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def _set_data(data, key, value):
    data[key] = value


def get_count_stats():
    sql_query = """
    SELECT 
        count(DISTINCT chat.id) as chat_count, 
        count(DISTINCT feedback.id) as feedback_count,
        count(DISTINCT session.id) as session_count
    FROM chat, feedback, session """
    with engine.connect() as conn:
        data = conn.execute(text(sql_query)).one()

    return dict(data._mapping)


def get_feedback_stats() -> dict:
    """
    return example: {'positive': 7, 'negative': 4, 'unknown': 2}
    """
    sql_query = """
SELECT pos.positive, neg.negative, ((SELECT COUNT(DISTINCT session.id) FROM session) - (neg.negative + pos.positive)) as unknown
FROM (SELECT COUNT(DISTINCT id) as positive FROM feedback WHERE is_helpful is TRUE) as pos,
(SELECT COUNT(DISTINCT id) as negative FROM feedback WHERE is_helpful is FALSE) as neg
"""

    with engine.connect() as conn:
        data = conn.execute(text(sql_query)).one()

    return dict(data._mapping)


def get_user_session_stats(year: int):
    with engine.connect() as conn:
        session_stats = _get_session_stats(conn, year)
        positive_feedback_stats, negative_feedback_stats = _get_feedback_for_stats(conn, year)

    return {
        'session': session_stats,
        'positive_feedback': positive_feedback_stats,
        'negative_feedback': negative_feedback_stats
    }


def _get_session_stats(conn, year: int) -> dict:
    data = conn.execute(text("SELECT * FROM session WHERE date_part('year', created_at) = :year"), year=year)

    chat_sessions = [ChatSession(**dict(row)) for row in data]

    # Set all months to 0
    month_sessions = {}
    [_set_data(month_sessions, i, 0) for i in MONTHS]

    for session in chat_sessions:
        for month in MONTHS:
            if session.created_at.strftime("%B") == month:
                month_sessions[month] = month_sessions[month] + 1

    return month_sessions


def _get_feedback_for_stats(conn, year: int) -> tuple[dict, dict]:
    data = conn.execute(text("SELECT * FROM feedback WHERE date_part('year', created_at) = :year"), year=year)

    # Set all months to 0
    monthly_positive_feedback = {}
    monthly_negative_feedback = {}
    [_set_data(monthly_positive_feedback, i, 0) for i in MONTHS]
    [_set_data(monthly_negative_feedback, i, 0) for i in MONTHS]

    chat_feedback = [Feedback(**dict(row)) for row in data]
    for feedback in chat_feedback:
        for month in MONTHS:
            if feedback.created_at.strftime("%B") == month:
                if feedback.is_helpful:
                    monthly_positive_feedback[month] = monthly_positive_feedback[month] + 1
                else:
                    monthly_negative_feedback[month] = monthly_negative_feedback[month] + 1

    return monthly_positive_feedback, monthly_negative_feedback
