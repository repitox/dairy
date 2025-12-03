"""
Миграция: Создание таблицы тегов
Дата: 2025-03-03 12:00:00
Описание: Добавляет таблицу tags для хранения тегов проектов
"""


def up(cursor):
    """Применить миграцию: создать таблицу tags и индексы"""
    # Создаём таблицу тегов
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tags (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            background_color TEXT NOT NULL DEFAULT '#6366f1',
            project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            created_by_id INTEGER NOT NULL REFERENCES users(id),
            created_at TEXT,
            active BOOLEAN DEFAULT TRUE,
            UNIQUE (project_id, name)
        );
        """
    )

    # Индексы для производительности
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tags_project_id ON tags(project_id);
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tags_created_by_id ON tags(created_by_id);
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tags_active ON tags(active);
        """
    )

    # Комментарии к таблице и столбцам
    try:
        cursor.execute("COMMENT ON TABLE tags IS 'Теги для задач, встреч и покупок в проектах';")
        cursor.execute("COMMENT ON COLUMN tags.name IS 'Название тега (может содержать эмодзи)';")
        cursor.execute("COMMENT ON COLUMN tags.background_color IS 'Цвет фона тега (hex формат)';")
        cursor.execute("COMMENT ON COLUMN tags.project_id IS 'ID проекта (projects.id)';")
        cursor.execute("COMMENT ON COLUMN tags.created_by_id IS 'ID пользователя, создавшего тег (users.id)';")
        cursor.execute("COMMENT ON COLUMN tags.active IS 'Статус активности тега';")
    except Exception:
        pass


def down(cursor):
    """Откатить миграцию: удалить таблицу tags"""
    cursor.execute("DROP TABLE IF EXISTS tags CASCADE;")
