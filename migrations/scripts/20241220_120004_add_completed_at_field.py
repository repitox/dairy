"""
Добавление поля completed_at в таблицу tasks
"""

def up(cursor):
    """Применить миграцию"""
    
    # Проверяем, есть ли уже поле completed_at
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'completed_at';
    """)
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE tasks ADD COLUMN completed_at TEXT;")
        print("✅ Добавлено поле completed_at в tasks")
    else:
        print("ℹ️ Поле completed_at уже существует")


def down(cursor):
    """Откатить миграцию"""
    
    cursor.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS completed_at;")
    print("✅ Поле completed_at удалено из tasks")