#!/usr/bin/env python3
"""
🔄 Миграция базы данных для Dashboard навигации
Обновляет структуру БД для поддержки новых функций
"""

import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def migrate_database():
    """Выполнить миграцию базы данных"""
    print("🔄 Начинаем миграцию базы данных для Dashboard...")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                
                # 1. Создаем таблицу purchases (если её нет) или обновляем shopping
                print("📦 Обновляем таблицу покупок...")
                
                # Проверяем, существует ли таблица purchases
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'purchases'
                    );
                """)
                result = cur.fetchone()
                purchases_exists = result['exists'] if result else False
                
                if not purchases_exists:
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
                    
                    print("✅ Таблица purchases создана на основе shopping")
                else:
                    print("ℹ️ Таблица purchases уже существует")
                
                # 2. Добавляем недостающие поля в purchases (если их нет)
                print("🔧 Проверяем поля в таблице purchases...")
                
                # Проверяем наличие поля price
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'purchases' AND column_name = 'price';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE purchases ADD COLUMN price DECIMAL(10,2);")
                    print("✅ Добавлено поле price")
                
                # Проверяем наличие поля category
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'purchases' AND column_name = 'category';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE purchases ADD COLUMN category TEXT DEFAULT 'other';")
                    print("✅ Добавлено поле category")
                
                # Проверяем наличие поля completed
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'purchases' AND column_name = 'completed';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE purchases ADD COLUMN completed BOOLEAN DEFAULT false;")
                    print("✅ Добавлено поле completed")
                
                # 3. Обновляем таблицу events для поддержки встреч
                print("📅 Обновляем таблицу событий...")
                
                # Добавляем поле type для типа события
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'events' AND column_name = 'type';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE events ADD COLUMN type TEXT DEFAULT 'other';")
                    print("✅ Добавлено поле type в events")
                
                # Добавляем поле participants для участников
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'events' AND column_name = 'participants';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE events ADD COLUMN participants TEXT;")
                    print("✅ Добавлено поле participants в events")
                
                # 4. Обновляем таблицу tasks для лучшей поддержки
                print("📋 Обновляем таблицу задач...")
                
                # Добавляем поле priority для приоритета
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'tasks' AND column_name = 'priority';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'medium';")
                    print("✅ Добавлено поле priority в tasks")
                
                # Добавляем поле category для категории задач
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'tasks' AND column_name = 'category';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT 'general';")
                    print("✅ Добавлено поле category в tasks")
                
                # 5. Добавляем индексы для производительности
                print("🚀 Добавляем индексы для производительности...")
                
                # Индексы для быстрого поиска по пользователю
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases(user_id);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
                """)
                
                # Индексы для фильтрации
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_purchases_completed ON purchases(completed);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_events_start_at ON events(start_at);
                """)
                
                print("✅ Индексы добавлены")
                
                # 6. Добавляем настройки по умолчанию для существующих пользователей
                print("⚙️ Добавляем настройки по умолчанию...")
                
                # Получаем всех пользователей без настроек темы
                cur.execute("""
                    SELECT DISTINCT u.telegram_id 
                    FROM users u 
                    LEFT JOIN user_settings us ON u.telegram_id = us.user_id AND us.key = 'theme'
                    WHERE us.user_id IS NULL;
                """)
                users_without_theme = cur.fetchall()
                
                # Добавляем настройки по умолчанию
                for user in users_without_theme:
                    user_id = user['user_id']
                    
                    # Тема по умолчанию
                    cur.execute("""
                        INSERT INTO user_settings (user_id, key, value) 
                        VALUES (%s, 'theme', 'auto')
                        ON CONFLICT (user_id, key) DO NOTHING;
                    """, (user_id,))
                    
                    # Email уведомления по умолчанию
                    cur.execute("""
                        INSERT INTO user_settings (user_id, key, value) 
                        VALUES (%s, 'email_notifications', 'false')
                        ON CONFLICT (user_id, key) DO NOTHING;
                    """, (user_id,))
                    
                    # Напоминания о задачах по умолчанию
                    cur.execute("""
                        INSERT INTO user_settings (user_id, key, value) 
                        VALUES (%s, 'task_reminders', 'true')
                        ON CONFLICT (user_id, key) DO NOTHING;
                    """, (user_id,))
                
                if users_without_theme:
                    print(f"✅ Добавлены настройки по умолчанию для {len(users_without_theme)} пользователей")
                else:
                    print("ℹ️ Все пользователи уже имеют настройки")
                
                # 7. Создаем представления для удобства
                print("👁️ Создаем представления для удобства...")
                
                # Представление для активных задач
                cur.execute("""
                    CREATE OR REPLACE VIEW active_tasks AS
                    SELECT * FROM tasks WHERE completed = false;
                """)
                
                # Представление для предстоящих событий
                cur.execute("""
                    CREATE OR REPLACE VIEW upcoming_events AS
                    SELECT * FROM events 
                    WHERE start_at >= CURRENT_DATE::text AND active = true
                    ORDER BY start_at;
                """)
                
                # Представление для активных покупок
                cur.execute("""
                    CREATE OR REPLACE VIEW active_purchases AS
                    SELECT * FROM purchases WHERE completed = false;
                """)
                
                print("✅ Представления созданы")
                
                conn.commit()
                print("🎉 Миграция успешно завершена!")
                
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        raise

def check_migration_status():
    """Проверить статус миграции"""
    print("🔍 Проверяем статус миграции...")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                
                # Проверяем таблицы
                cur.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name;
                """)
                tables = [row['table_name'] for row in cur.fetchall()]
                print(f"📊 Таблицы в БД: {', '.join(tables)}")
                
                # Проверяем поля в purchases
                if 'purchases' in tables:
                    cur.execute("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_name = 'purchases'
                        ORDER BY ordinal_position;
                    """)
                    columns = cur.fetchall()
                    print("📦 Поля в таблице purchases:")
                    for col in columns:
                        print(f"   - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
                
                # Проверяем настройки пользователей
                cur.execute("""
                    SELECT key, COUNT(*) as count 
                    FROM user_settings 
                    GROUP BY key 
                    ORDER BY key;
                """)
                settings = cur.fetchall()
                print("⚙️ Настройки пользователей:")
                for setting in settings:
                    print(f"   - {setting['key']}: {setting['count']} пользователей")
                
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")

if __name__ == "__main__":
    print("🚀 Миграция Dashboard навигации")
    print("=" * 50)
    
    # Проверяем текущий статус
    check_migration_status()
    print()
    
    # Выполняем миграцию
    migrate_database()
    print()
    
    # Проверяем результат
    print("📋 Результат миграции:")
    check_migration_status()
    
    print("\n🎉 Миграция завершена! Dashboard готов к использованию.")