#!/usr/bin/env python3
"""
Скрипт для исправления таблицы purchases на продакшн сервере NetAngels
Запускать на сервере: python3 fix_production_purchases.py
"""

from db import get_conn

def check_and_fix_purchases_table():
    """Проверить и исправить таблицу purchases"""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                print("🔍 Проверяем состояние базы данных...")
                
                # 1. Проверяем все таблицы
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
                tables = [row[0] for row in cur.fetchall()]
                print(f"📋 Таблицы в базе: {tables}")
                
                # 2. Проверяем, есть ли таблица purchases
                purchases_exists = 'purchases' in tables
                shopping_items_exists = 'shopping_items' in tables
                
                print(f"📊 Таблица purchases: {'✅ есть' if purchases_exists else '❌ нет'}")
                print(f"📊 Таблица shopping_items: {'✅ есть' if shopping_items_exists else '❌ нет'}")
                
                # 3. Если purchases не существует, но есть shopping_items - возможно, используется другое название
                if not purchases_exists and shopping_items_exists:
                    print("🔄 Возможно, используется таблица shopping_items вместо purchases")
                    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'shopping_items' ORDER BY ordinal_position;")
                    columns = [row[0] for row in cur.fetchall()]
                    print(f"📋 Поля shopping_items: {columns}")
                    
                    # Проверяем, есть ли нужные поля
                    has_shopping_list_id = 'shopping_list_id' in columns
                    has_url = 'url' in columns
                    has_comment = 'comment' in columns
                    
                    print(f"🔍 shopping_list_id: {'✅' if has_shopping_list_id else '❌'}")
                    print(f"🔍 url: {'✅' if has_url else '❌'}")
                    print(f"🔍 comment: {'✅' if has_comment else '❌'}")
                    
                    # Добавляем недостающие поля
                    if not has_shopping_list_id:
                        print("➕ Добавляем поле shopping_list_id...")
                        cur.execute("ALTER TABLE shopping_items ADD COLUMN shopping_list_id INTEGER;")
                    
                    if not has_url:
                        print("➕ Добавляем поле url...")
                        cur.execute("ALTER TABLE shopping_items ADD COLUMN url TEXT;")
                    
                    if not has_comment:
                        print("➕ Добавляем поле comment...")
                        cur.execute("ALTER TABLE shopping_items ADD COLUMN comment TEXT;")
                    
                    # Создаем индексы
                    print("📝 Создаем индексы...")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_shopping_items_shopping_list_id ON shopping_items(shopping_list_id);")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_shopping_items_user_id ON shopping_items(user_id);")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_shopping_items_completed ON shopping_items(completed);")
                    
                    conn.commit()
                    print("✅ Таблица shopping_items обновлена!")
                
                # 4. Если purchases существует
                elif purchases_exists:
                    print("🔍 Проверяем структуру таблицы purchases...")
                    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'purchases' ORDER BY ordinal_position;")
                    columns = [row[0] for row in cur.fetchall()]
                    print(f"📋 Поля purchases: {columns}")
                    
                    # Проверяем последовательность
                    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_sequences WHERE sequencename = 'purchases_id_seq');")
                    seq_exists = cur.fetchone()[0]
                    print(f"🔢 Последовательность purchases_id_seq: {'✅' if seq_exists else '❌'}")
                    
                    if not seq_exists:
                        print("➕ Создаем последовательность...")
                        cur.execute("CREATE SEQUENCE purchases_id_seq;")
                        cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM purchases;")
                        next_val = cur.fetchone()[0]
                        cur.execute(f"SELECT setval('purchases_id_seq', {next_val}, false);")
                        cur.execute("ALTER TABLE purchases ALTER COLUMN id SET DEFAULT nextval('purchases_id_seq');")
                        cur.execute("ALTER SEQUENCE purchases_id_seq OWNED BY purchases.id;")
                    
                    # Добавляем недостающие поля
                    has_shopping_list_id = 'shopping_list_id' in columns
                    has_url = 'url' in columns
                    has_comment = 'comment' in columns
                    
                    if not has_shopping_list_id:
                        print("➕ Добавляем поле shopping_list_id...")
                        cur.execute("ALTER TABLE purchases ADD COLUMN shopping_list_id INTEGER;")
                    
                    if not has_url:
                        print("➕ Добавляем поле url...")
                        cur.execute("ALTER TABLE purchases ADD COLUMN url TEXT;")
                    
                    if not has_comment:
                        print("➕ Добавляем поле comment...")
                        cur.execute("ALTER TABLE purchases ADD COLUMN comment TEXT;")
                    
                    # Создаем индексы
                    print("📝 Создаем индексы...")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_purchases_shopping_list_id ON purchases(shopping_list_id);")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases(user_id);")
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_purchases_completed ON purchases(completed);")
                    
                    conn.commit()
                    print("✅ Таблица purchases обновлена!")
                
                # 5. Если ни одной таблицы нет - создаем purchases
                else:
                    print("🆕 Создаем таблицу purchases...")
                    cur.execute("""
                        CREATE TABLE purchases (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER NOT NULL REFERENCES users(id),
                            project_id INTEGER REFERENCES projects(id),
                            name TEXT NOT NULL,
                            quantity INTEGER NOT NULL DEFAULT 1,
                            price DECIMAL(10,2),
                            category TEXT DEFAULT 'other',
                            completed BOOLEAN DEFAULT FALSE,
                            created_at TEXT,
                            shopping_list_id INTEGER,
                            url TEXT,
                            comment TEXT
                        );
                    """)
                    
                    # Создаем индексы
                    cur.execute("CREATE INDEX idx_purchases_user_id ON purchases(user_id);")
                    cur.execute("CREATE INDEX idx_purchases_shopping_list_id ON purchases(shopping_list_id);")
                    cur.execute("CREATE INDEX idx_purchases_completed ON purchases(completed);")
                    
                    conn.commit()
                    print("✅ Таблица purchases создана!")
                
                # 6. Отмечаем миграцию как выполненную
                print("📝 Отмечаем миграцию как выполненную...")
                cur.execute("""
                    INSERT INTO migrations (version, name, executed_at) 
                    VALUES (%s, %s, NOW()) 
                    ON CONFLICT (version) DO NOTHING;
                """, ('20250127_000001', 'fix_purchases_table'))
                conn.commit()
                
                print("🎉 Исправление завершено успешно!")
                
                # 7. Финальная проверка
                print("\n📊 Финальная проверка:")
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('purchases', 'shopping_items') ORDER BY table_name;")
                final_tables = [row[0] for row in cur.fetchall()]
                for table in final_tables:
                    cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position;")
                    columns = [row[0] for row in cur.fetchall()]
                    print(f"  📋 {table}: {columns}")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_and_fix_purchases_table()