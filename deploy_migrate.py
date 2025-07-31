#!/usr/bin/env python3
"""
🚀 Автоматическая миграция для деплоя
Проверяет и выполняет необходимые миграции базы данных
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def check_migration_needed():
    """Проверить, нужна ли миграция"""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Проверяем, существует ли таблица purchases
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'purchases'
                    );
                """)
                result = cur.fetchone()
                purchases_exists = result['exists'] if result else False
                
                # Проверяем, есть ли поле type в events
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'events' AND column_name = 'type';
                """)
                events_type_exists = cur.fetchone() is not None
                
                # Проверяем, есть ли настройки пользователей
                cur.execute("SELECT COUNT(*) as count FROM user_settings WHERE key = 'theme'")
                theme_settings_count = cur.fetchone()['count']
                
                return {
                    'purchases_table': purchases_exists,
                    'events_type_field': events_type_exists,
                    'user_settings': theme_settings_count > 0,
                    'migration_needed': not (purchases_exists and events_type_exists)
                }
    except Exception as e:
        print(f"❌ Ошибка проверки миграции: {e}")
        return {'migration_needed': True, 'error': str(e)}

def run_migration():
    """Выполнить миграцию базы данных"""
    print("🔄 Выполняем миграцию базы данных...")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                
                # 1. Создаем таблицу purchases (если её нет)
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'purchases'
                    );
                """)
                result = cur.fetchone()
                purchases_exists = result['exists'] if result else False
                
                if not purchases_exists:
                    print("📦 Создаем таблицу purchases...")
                    # Создаем таблицу purchases на основе shopping
                    cur.execute("""
                        CREATE TABLE purchases AS 
                        SELECT 
                            id,
                            user_id,
                            project_id,
                            item as name,
                            quantity,
                            CASE 
                                WHEN status = 'Куплено' THEN true 
                                ELSE false 
                            END as completed,
                            created_at,
                            NULL::DECIMAL as price,
                            'other'::TEXT as category
                        FROM shopping;
                    """)
                    
                    # Добавляем первичный ключ и ограничения
                    cur.execute("ALTER TABLE purchases ADD PRIMARY KEY (id);")
                    cur.execute("ALTER TABLE purchases ALTER COLUMN name SET NOT NULL;")
                    cur.execute("ALTER TABLE purchases ALTER COLUMN quantity SET NOT NULL;")
                    cur.execute("ALTER TABLE purchases ALTER COLUMN completed SET DEFAULT false;")
                    print("✅ Таблица purchases создана")
                
                # 2. Добавляем поля в events
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'events' AND column_name = 'type';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE events ADD COLUMN type TEXT DEFAULT 'other';")
                    print("✅ Добавлено поле type в events")
                
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'events' AND column_name = 'participants';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE events ADD COLUMN participants TEXT;")
                    print("✅ Добавлено поле participants в events")
                
                # 3. Добавляем поля в tasks
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'tasks' AND column_name = 'category';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT 'general';")
                    print("✅ Добавлено поле category в tasks")
                
                # 4. Создаем индексы
                cur.execute("CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases(user_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_purchases_completed ON purchases(completed);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_events_start_at ON events(start_at);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);")
                print("✅ Индексы созданы")
                
                # 5. Добавляем настройки по умолчанию для пользователей без настроек
                cur.execute("""
                    SELECT DISTINCT u.telegram_id 
                    FROM users u 
                    LEFT JOIN user_settings us ON u.telegram_id = us.user_id AND us.key = 'theme'
                    WHERE us.user_id IS NULL;
                """)
                users_without_theme = cur.fetchall()
                
                for user in users_without_theme:
                    user_id = user['telegram_id']
                    
                    cur.execute("""
                        INSERT INTO user_settings (user_id, key, value) 
                        VALUES (%s, 'theme', 'auto')
                        ON CONFLICT (user_id, key) DO NOTHING;
                    """, (user_id,))
                    
                    cur.execute("""
                        INSERT INTO user_settings (user_id, key, value) 
                        VALUES (%s, 'email_notifications', 'false')
                        ON CONFLICT (user_id, key) DO NOTHING;
                    """, (user_id,))
                    
                    cur.execute("""
                        INSERT INTO user_settings (user_id, key, value) 
                        VALUES (%s, 'task_reminders', 'true')
                        ON CONFLICT (user_id, key) DO NOTHING;
                    """, (user_id,))
                
                if users_without_theme:
                    print(f"✅ Добавлены настройки для {len(users_without_theme)} пользователей")
                
                conn.commit()
                print("🎉 Миграция успешно завершена!")
                return True
                
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        return False

def main():
    """Главная функция"""
    print("🚀 Проверка необходимости миграции...")
    
    # Проверяем подключение к БД
    try:
        with get_conn() as conn:
            print("✅ Подключение к базе данных установлено")
    except Exception as e:
        print(f"❌ Не удалось подключиться к базе данных: {e}")
        sys.exit(1)
    
    # Проверяем, нужна ли миграция
    status = check_migration_needed()
    
    if 'error' in status:
        print(f"❌ Ошибка при проверке: {status['error']}")
        sys.exit(1)
    
    if not status['migration_needed']:
        print("✅ Миграция не требуется - база данных уже обновлена")
        print(f"   - Таблица purchases: {'✅' if status['purchases_table'] else '❌'}")
        print(f"   - Поле events.type: {'✅' if status['events_type_field'] else '❌'}")
        print(f"   - Настройки пользователей: {'✅' if status['user_settings'] else '❌'}")
        return
    
    print("🔄 Миграция необходима")
    print(f"   - Таблица purchases: {'✅' if status['purchases_table'] else '❌ требуется'}")
    print(f"   - Поле events.type: {'✅' if status['events_type_field'] else '❌ требуется'}")
    print(f"   - Настройки пользователей: {'✅' if status['user_settings'] else '❌ требуется'}")
    
    # Выполняем миграцию
    success = run_migration()
    
    if success:
        print("🎉 Деплой готов! Dashboard полностью функционален.")
        sys.exit(0)
    else:
        print("❌ Миграция не удалась")
        sys.exit(1)

if __name__ == "__main__":
    main()