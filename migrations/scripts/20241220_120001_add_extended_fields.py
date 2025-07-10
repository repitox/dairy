"""
Добавление расширенных полей в существующие таблицы
"""

def up(cursor):
    """Применить миграцию"""
    
    # Добавляем поля в events
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'events' AND column_name = 'type';
    """)
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE events ADD COLUMN type TEXT DEFAULT 'other';")
        print("✅ Добавлено поле type в events")
    
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'events' AND column_name = 'participants';
    """)
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE events ADD COLUMN participants TEXT;")
        print("✅ Добавлено поле participants в events")
    
    # Добавляем поля в tasks
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'category';
    """)
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT 'general';")
        print("✅ Добавлено поле category в tasks")
    
    # Создаем индексы для производительности
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_start_at ON events(start_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopping_user_id ON shopping(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopping_status ON shopping(status);")
    
    print("✅ Индексы созданы")


def down(cursor):
    """Откатить миграцию"""
    
    # Удаляем добавленные поля
    cursor.execute("ALTER TABLE events DROP COLUMN IF EXISTS type;")
    cursor.execute("ALTER TABLE events DROP COLUMN IF EXISTS participants;")
    cursor.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS category;")
    
    # Удаляем индексы
    cursor.execute("DROP INDEX IF EXISTS idx_events_user_id;")
    cursor.execute("DROP INDEX IF EXISTS idx_events_start_at;")
    cursor.execute("DROP INDEX IF EXISTS idx_tasks_user_id;")
    cursor.execute("DROP INDEX IF EXISTS idx_tasks_completed;")
    cursor.execute("DROP INDEX IF EXISTS idx_shopping_user_id;")
    cursor.execute("DROP INDEX IF EXISTS idx_shopping_status;")
    
    print("✅ Расширенные поля и индексы удалены")