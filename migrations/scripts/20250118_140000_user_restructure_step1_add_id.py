"""
Миграция: Добавление автоинкрементного поля id в таблицу users
Этап 1: Подготовка новой структуры
"""

def upgrade(cursor):
    print("🔄 Этап 1: Добавление автоинкрементного поля id в таблицу users")
    
    # Создаём sequence при необходимости
    cursor.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'users_id_seq') THEN
                CREATE SEQUENCE users_id_seq;
            END IF;
        END $$;
    """)

    # Добавляем поле id, если его нет
    cursor.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS id INTEGER
    """)

    # Назначаем default от sequence и заполняем значения для существующих строк
    cursor.execute("""
        ALTER TABLE users 
        ALTER COLUMN id SET DEFAULT nextval('users_id_seq')
    """)
    cursor.execute("""
        UPDATE users SET id = nextval('users_id_seq')
        WHERE id IS NULL
    """)
    cursor.execute("""
        ALTER SEQUENCE users_id_seq OWNED BY users.id
    """)
    
    # Создаем временный уникальный индекс для telegram_id/user_id (что доступно)
    cursor.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'user_id'
            ) THEN
                EXECUTE 'CREATE UNIQUE INDEX IF NOT EXISTS idx_users_telegram_id ON users(user_id)';
            ELSIF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'telegram_id'
            ) THEN
                EXECUTE 'CREATE UNIQUE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)';
            END IF;
        END $$;
        """
    )
    
    print("✅ Поле id добавлено и заполнено в таблице users")

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