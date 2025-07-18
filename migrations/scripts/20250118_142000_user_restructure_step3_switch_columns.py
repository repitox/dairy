"""
Миграция: Переключение на новые колонки
Этап 3: Замена старых колонок на новые
"""

def upgrade(cursor):
    print("🔄 Этап 3: Переключение на новые колонки")
    
    # Список таблиц и их колонок для обновления
    tables_to_update = [
        ('events', 'user_id'),
        ('notes', 'user_id'),
        ('project_members', 'user_id'),
        ('projects', 'owner_id'),
        ('purchases', 'user_id'),
        ('reminder_logs', 'user_id'),
        ('shopping', 'user_id'),
        ('shopping_lists', 'user_id'),
        ('tasks', 'user_id'),
        ('user_settings', 'user_id')
    ]
    
    for table_name, column_name in tables_to_update:
        # Удаляем старую колонку
        cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
        
        # Переименовываем временную колонку
        cursor.execute(f"""
            ALTER TABLE {table_name} 
            RENAME COLUMN temp_user_id TO {column_name}
        """)
        
        # Добавляем NOT NULL ограничение
        cursor.execute(f"""
            ALTER TABLE {table_name} 
            ALTER COLUMN {column_name} SET NOT NULL
        """)
        
        print(f"✅ Колонка {column_name} обновлена в таблице {table_name}")
    
    print("✅ Все колонки переключены на новые значения")

def downgrade(cursor):
    print("🔄 Откат: Возврат к старым колонкам")
    
    # Откат сложный, поэтому лучше использовать резервную копию
    print("⚠️  Откат этого этапа требует восстановления из резервной копии")
    print("⚠️  Используйте резервную копию для восстановления")