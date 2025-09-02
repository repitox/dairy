"""
Скрипт миграции для продакшена: добавление таблицы birthdays
"""
from app.database.connection import get_db_connection


def run():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS birthdays (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    full_name TEXT NOT NULL,
                    day INTEGER NOT NULL CHECK (day BETWEEN 1 AND 31),
                    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
                    year INTEGER,
                    description TEXT,
                    created_at TEXT
                );
                """
            )
            conn.commit()
    print("✅ Миграция birthdays выполнена")


if __name__ == "__main__":
    run()

