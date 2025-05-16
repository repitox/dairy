import sqlite3
from pathlib import Path

DB_PATH = Path("data.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                registered_at TEXT
            )
        """)
        conn.commit()

def add_user(user_id: int, first_name: str, username: str):
    from datetime import datetime
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, first_name, username, registered_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, first_name, username, datetime.utcnow().isoformat()))
        conn.commit()

def get_all_users():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, first_name, username, registered_at FROM users ORDER BY registered_at DESC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "user_id": r[0],
                "first_name": r[1],
                "username": r[2],
                "registered_at": r[3]
            })
        return result