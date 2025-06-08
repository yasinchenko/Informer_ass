# file: database/crud.py
import sqlite3
from database.models import LogMessage


def init_db(db_file: str):
    with sqlite3.connect(db_file) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                chat_id INTEGER,
                message_id INTEGER,
                user_id INTEGER,
                username TEXT,
                text TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()


def insert_message(db_file: str, msg: LogMessage):
    with sqlite3.connect(db_file) as conn:
        conn.execute('''
            INSERT INTO messages (chat_id, message_id, user_id, username, text, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            msg.chat_id,
            msg.message_id,
            msg.user_id,
            msg.username,
            msg.text,
            msg.timestamp
        ))
        conn.commit()


def get_texts_by_chat_and_date(db_file: str, chat_id: int, from_date: str, to_date: str) -> list[str]:
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT text FROM messages
            WHERE chat_id = ? AND date(timestamp) BETWEEN date(?) AND date(?)
        ''', (chat_id, from_date, to_date))
        return [row[0] for row in cursor.fetchall()]
