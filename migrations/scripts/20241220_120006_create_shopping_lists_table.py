"""
Создание таблицы shopping_lists и обновление таблицы purchases
"""

def up(cursor):
    """Применить миграцию"""
    
    # Создаем таблицу списков покупок
    print("📋 Создаем таблицу shopping_lists...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shopping_lists (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            project_id INTEGER NOT NULL,
            user_id BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
    """)
    
    # Создаем индексы
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopping_lists_user_id ON shopping_lists(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopping_lists_project_id ON shopping_lists(project_id);")
    
    # Проверяем, существует ли столбец shopping_list_id в таблице purchases
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'purchases' AND column_name = 'shopping_list_id';
    """)
    column_exists = cursor.fetchone()
    
    if not column_exists:
        print("🔗 Добавляем связь со списками в таблицу purchases...")
        # Добавляем столбец для связи со списком покупок
        cursor.execute("""
            ALTER TABLE purchases 
            ADD COLUMN shopping_list_id INTEGER,
            ADD COLUMN url TEXT,
            ADD COLUMN comment TEXT;
        """)
        
        # Добавляем внешний ключ
        cursor.execute("""
            ALTER TABLE purchases 
            ADD CONSTRAINT fk_purchases_shopping_list 
            FOREIGN KEY (shopping_list_id) REFERENCES shopping_lists(id) ON DELETE SET NULL;
        """)
        
        # Создаем индекс
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_shopping_list_id ON purchases(shopping_list_id);")
    
    # Создаем дефолтный список для существующих покупок
    print("📝 Создаем дефолтные списки для существующих пользователей...")
    cursor.execute("""
        INSERT INTO shopping_lists (name, project_id, user_id, created_at)
        SELECT DISTINCT 
            'Общий список' as name,
            COALESCE(p.project_id, (
                SELECT id FROM projects 
                WHERE owner_id = p.user_id 
                ORDER BY created_at ASC 
                LIMIT 1
            )) as project_id,
            p.user_id,
            CURRENT_TIMESTAMP
        FROM purchases p
        WHERE NOT EXISTS (
            SELECT 1 FROM shopping_lists sl 
            WHERE sl.user_id = p.user_id
        )
        AND p.user_id IS NOT NULL;
    """)
    
    # Привязываем существующие покупки к дефолтному списку
    cursor.execute("""
        UPDATE purchases 
        SET shopping_list_id = (
            SELECT sl.id 
            FROM shopping_lists sl 
            WHERE sl.user_id = purchases.user_id 
            AND sl.name = 'Общий список'
            LIMIT 1
        )
        WHERE shopping_list_id IS NULL;
    """)
    
    print("✅ Таблица shopping_lists создана и настроена")


def down(cursor):
    """Откатить миграцию"""
    
    # Удаляем внешний ключ и столбцы из purchases
    cursor.execute("ALTER TABLE purchases DROP CONSTRAINT IF EXISTS fk_purchases_shopping_list;")
    cursor.execute("ALTER TABLE purchases DROP COLUMN IF EXISTS shopping_list_id;")
    cursor.execute("ALTER TABLE purchases DROP COLUMN IF EXISTS url;")
    cursor.execute("ALTER TABLE purchases DROP COLUMN IF EXISTS comment;")
    
    # Удаляем таблицу списков покупок
    cursor.execute("DROP TABLE IF EXISTS shopping_lists CASCADE;")
    
    print("✅ Миграция shopping_lists откачена")