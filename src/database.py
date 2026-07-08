import sqlite3
import os
from datetime import datetime

DB_PATH = "./data/chat_history.db"

def init_db():
    """Create database and table if not exists."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT NOT NULL,
            question  TEXT NOT NULL,
            answer    TEXT NOT NULL,
            sources   TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_chat(username: str, question: str, answer: str, sources: str):
    """Save a Q&A interaction to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (username, question, answer, sources, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (username, question, answer, sources, datetime.now()))
    conn.commit()
    conn.close()

def get_chat_history(username: str = None):
    """Fetch chat history — all or by username."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if username:
        cursor.execute("""
            SELECT id, username, question, answer, sources, timestamp
            FROM chat_history
            WHERE username = ?
            ORDER BY timestamp DESC
        """, (username,))
    else:
        cursor.execute("""
            SELECT id, username, question, answer, sources, timestamp
            FROM chat_history
            ORDER BY timestamp DESC
        """)
    rows = cursor.fetchall()
    conn.close()
    return rows