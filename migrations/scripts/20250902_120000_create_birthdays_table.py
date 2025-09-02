"""
Миграция: Создание таблицы дней рождения
Дата: 2025-09-02 12:00:00
Описание: Добавляет таблицу birthdays, если её нет, и необходимые индексы
"""


def up(cursor):
    """Применить миграцию: создать таблицу birthdays и индексы"""
    # Создаём таблицу, если отсутствует
    cursor.execute(
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

    # Индексы для производительности по user_id и дате
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_birthdays_user_id ON birthdays(user_id);
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_birthdays_month_day ON birthdays(month, day);
        """
    )

    # Комментарии к таблице и столбцам (не обязательно, но полезно)
    try:
        cursor.execute("COMMENT ON TABLE birthdays IS 'Дни рождения пользователей';")
        cursor.execute("COMMENT ON COLUMN birthdays.user_id IS 'ID пользователя (users.id)';")
    except Exception:
        # В некоторых БД/конфигурациях COMMENT может быть недоступен
        pass


def down(cursor):
    """Откатить миграцию: удалить таблицу birthdays"""
    cursor.execute("DROP TABLE IF EXISTS birthdays CASCADE;")