"""
Создание таблицы заметок
"""

def up(cursor):
    """Применить миграцию"""
    
    # Заметки
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Индекс для быстрого поиска заметок пользователя
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);
    """)
    
    # Индекс для сортировки по дате создания
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at DESC);
    """)

    print("✅ Таблица заметок создана")


def down(cursor):
    """Откатить миграцию"""
    
    cursor.execute("DROP INDEX IF EXISTS idx_notes_created_at;")
    cursor.execute("DROP INDEX IF EXISTS idx_notes_user_id;")
    cursor.execute("DROP TABLE IF EXISTS notes CASCADE;")
    
    print("✅ Таблица заметок удалена")