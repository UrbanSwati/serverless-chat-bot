from configuration import engine
from sqlalchemy import text


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