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
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS shopping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            created_at TEXT
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
    
def add_purchase(user_id: int, item: str, quantity: int):
    from datetime import datetime
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO shopping (user_id, item, quantity, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, item, quantity, datetime.utcnow().isoformat()))
        conn.commit()

def get_all_purchases():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT item, quantity, created_at FROM shopping ORDER BY created_at DESC")
        return cursor.fetchall()
    
def get_purchases_by_status(status_filter: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if status_filter == "Все":
            cursor.execute("""
                SELECT id, item, quantity, status, created_at
                FROM shopping
                ORDER BY created_at DESC
            """)
        else:
            cursor.execute("""
                SELECT id, item, quantity, status, created_at
                FROM shopping
                WHERE status = ?
                ORDER BY created_at DESC
            """, (status_filter,))
        return cursor.fetchall()