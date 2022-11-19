from datetime import datetime

from sqlalchemy import text


def insert_chat_record(conn, text_message: str, bot_response: str, session_uuid: str):
    created_at = datetime.utcnow()

    session_sql_text = """
    INSERT INTO session (session_uuid, created_at)
    VALUES (:uuid, :created_at) ON CONFLICT DO NOTHING
    """
    conn.execute(text(session_sql_text), uuid=session_uuid, created_at=created_at)

    chat_sql_text = """
    INSERT INTO chat (text_message, created_at, bot_response, session_id)
    VALUES (:text_message, :created_at, :bot_response, (SELECT id FROM session WHERE session_uuid=:uuid))
    """
    params = {
        "uuid": session_uuid,
        "created_at": created_at,
        "text_message": text_message,
        "bot_response": bot_response
    }
    conn.execute(text(chat_sql_text), params)


def insert_feedback(conn, session_uuid: str, is_helpful: bool):
    created_at = datetime.utcnow()

    sql_text = """
    INSERT INTO feedback (is_helpful, created_at, session_id)
    VALUES (:is_helpful, :created_at, (SELECT id FROM session WHERE session_uuid=:uuid))
    """

    params = {
        "is_helpful": is_helpful,
        "created_at": created_at,
        "uuid": session_uuid
    }

    conn.execute(text(sql_text), params)
