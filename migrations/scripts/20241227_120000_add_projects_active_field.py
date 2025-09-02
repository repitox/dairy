"""
Миграция: Добавление поля active в таблицу projects
Дата создания: 2024-12-27
"""

def upgrade(conn):
    """Добавляем поле active в таблицу projects"""
    print("🔄 Добавляем поле active в таблицу projects...")
    
    with conn.cursor() as cur:
        # Добавляем поле active со значением по умолчанию TRUE
        cur.execute("""
            ALTER TABLE projects 
            ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE
        """)
        
        # Обновляем все существующие проекты, устанавливая active = TRUE
        cur.execute("""
            UPDATE projects 
            SET active = TRUE 
            WHERE active IS NULL
        """)
        
        print("✅ Поле active успешно добавлено в таблицу projects")

def downgrade(conn):
    """Удаляем поле active из таблицы projects"""
    print("🔄 Удаляем поле active из таблицы projects...")
    
    with conn.cursor() as cur:
        cur.execute("""
            ALTER TABLE projects 
            DROP COLUMN IF EXISTS active
        """)
        
        print("✅ Поле active успешно удалено из таблицы projects")

# Совместимость с нашим MigrationManager (ожидает up(cursor)/down(cursor))

def up(cursor):
    # Менеджер передает курсор; адаптируем к upgrade(conn)
    return upgrade(cursor.connection)


def down(cursor):
    return downgrade(cursor.connection)