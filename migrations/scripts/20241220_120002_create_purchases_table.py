"""
Создание таблицы purchases на основе shopping с дополнительными полями
"""

def up(cursor):
    """Применить миграцию"""
    
    # Проверяем, существует ли таблица purchases
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'purchases'
        );
    """)
    result = cursor.fetchone()
    # result может быть кортежем или словарем в зависимости от курсора
    if hasattr(result, 'keys'):  # RealDictCursor
        purchases_exists = result['exists'] if result else False
    else:  # обычный курсор
        purchases_exists = result[0] if result else False
    
    if not purchases_exists:
        print("📦 Создаем таблицу purchases...")
        
        # Создаем таблицу purchases на основе shopping
        cursor.execute("""
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
        cursor.execute("ALTER TABLE purchases ADD PRIMARY KEY (id);")
        cursor.execute("ALTER TABLE purchases ALTER COLUMN name SET NOT NULL;")
        cursor.execute("ALTER TABLE purchases ALTER COLUMN quantity SET NOT NULL;")
        cursor.execute("ALTER TABLE purchases ALTER COLUMN completed SET DEFAULT false;")
        
        # Создаем индексы
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_completed ON purchases(completed);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_category ON purchases(category);")
        
        print("✅ Таблица purchases создана")
    else:
        print("ℹ️ Таблица purchases уже существует")


def down(cursor):
    """Откатить миграцию"""
    
    cursor.execute("DROP TABLE IF EXISTS purchases CASCADE;")
    print("✅ Таблица purchases удалена")