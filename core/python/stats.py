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
