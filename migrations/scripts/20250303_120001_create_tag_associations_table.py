"""
Миграция: Создание таблицы связей тегов
Дата: 2025-03-03 12:00:01
Описание: Добавляет таблицу tag_associations для связи тегов с задачами, встречами и покупками
"""


def up(cursor):
    """Применить миграцию: создать таблицу tag_associations и индексы"""
    # Создаём таблицу связей тегов с объектами
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tag_associations (
            id SERIAL PRIMARY KEY,
            tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
            object_type TEXT NOT NULL CHECK (object_type IN ('task', 'event', 'purchase')),
            object_id INTEGER NOT NULL,
            created_at TEXT,
            UNIQUE (tag_id, object_type, object_id)
        );
        """
    )

    # Индексы для производительности
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tag_associations_tag_id ON tag_associations(tag_id);
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tag_associations_object ON tag_associations(object_type, object_id);
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tag_associations_lookup ON tag_associations(tag_id, object_type, object_id);
        """
    )

    # Комментарии к таблице и столбцам
    try:
        cursor.execute("COMMENT ON TABLE tag_associations IS 'Связь тегов с задачами, встречами и покупками';")
        cursor.execute("COMMENT ON COLUMN tag_associations.tag_id IS 'ID тега (tags.id)';")
        cursor.execute("COMMENT ON COLUMN tag_associations.object_type IS 'Тип объекта (task, event, purchase)';")
        cursor.execute("COMMENT ON COLUMN tag_associations.object_id IS 'ID объекта (task_id, event_id или purchase_id)';")
    except Exception:
        pass


def down(cursor):
    """Откатить миграцию: удалить таблицу tag_associations"""
    cursor.execute("DROP TABLE IF EXISTS tag_associations CASCADE;")
