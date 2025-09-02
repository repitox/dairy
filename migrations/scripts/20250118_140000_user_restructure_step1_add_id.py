"""
Миграция: Добавление автоинкрементного поля id в таблицу users
Этап 1: Подготовка новой структуры
"""

def upgrade(cursor):
    print("🔄 Этап 1: Добавление автоинкрементного поля id в таблицу users")
    
    # Добавляем новое поле id
    cursor.execute("""
        ALTER TABLE users 
        ADD COLUMN id SERIAL
    """)
    
    # Создаем временный уникальный индекс для telegram_id
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_users_telegram_id 
        ON users(user_id)
    """)
    
    print("✅ Поле id добавлено в таблицу users")

def downgrade(cursor):
    print("🔄 Откат: Удаление поля id из таблицы users")
    
    # Удаляем индекс
    cursor.execute("DROP INDEX IF EXISTS idx_users_telegram_id")
    
    # Удаляем поле id
    cursor.execute("ALTER TABLE users DROP COLUMN IF EXISTS id")
    
    print("✅ Поле id удалено из таблицы users")

# Совместимость с MigrationManager (ожидает up(cursor)/down(cursor))

def up(cursor):
    return upgrade(cursor)


def down(cursor):
    return downgrade(cursor)