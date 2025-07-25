"""
Миграция: Финализация реструктуризации
Этап 4: Установка новых первичных ключей и переименование полей
"""

def upgrade(cursor):
    print("🔄 Этап 4: Финализация реструктуризации")
    
    # Переименовываем user_id в telegram_id в таблице users
    cursor.execute("""
        ALTER TABLE users 
        RENAME COLUMN user_id TO telegram_id
    """)
    
    # Удаляем старый первичный ключ
    cursor.execute("""
        ALTER TABLE users 
        DROP CONSTRAINT users_pkey
    """)
    
    # Устанавливаем новый первичный ключ
    cursor.execute("""
        ALTER TABLE users 
        ADD CONSTRAINT users_pkey PRIMARY KEY (id)
    """)
    
    # Добавляем уникальный индекс для telegram_id
    cursor.execute("""
        DROP INDEX IF EXISTS idx_users_telegram_id
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX idx_users_telegram_id 
        ON users(telegram_id)
    """)
    
    # Добавляем внешние ключи для всех связанных таблиц
    foreign_keys = [
        ('events', 'user_id', 'fk_events_user_id'),
        ('notes', 'user_id', 'fk_notes_user_id'),
        ('project_members', 'user_id', 'fk_project_members_user_id'),
        ('projects', 'owner_id', 'fk_projects_owner_id'),
        ('purchases', 'user_id', 'fk_purchases_user_id'),
        ('reminder_logs', 'user_id', 'fk_reminder_logs_user_id'),
        ('shopping', 'user_id', 'fk_shopping_user_id'),
        ('shopping_lists', 'user_id', 'fk_shopping_lists_user_id'),
        ('tasks', 'user_id', 'fk_tasks_user_id'),
        ('user_settings', 'user_id', 'fk_user_settings_user_id')
    ]
    
    for table_name, column_name, constraint_name in foreign_keys:
        cursor.execute(f"""
            ALTER TABLE {table_name} 
            ADD CONSTRAINT {constraint_name} 
            FOREIGN KEY ({column_name}) 
            REFERENCES users(id) 
            ON DELETE CASCADE
        """)
        print(f"✅ Внешний ключ добавлен для {table_name}.{column_name}")
    
    print("✅ Реструктуризация завершена!")
    print("📊 Новая структура:")
    print("   - users.id (PRIMARY KEY, SERIAL)")
    print("   - users.telegram_id (UNIQUE, bigint)")
    print("   - Все связанные таблицы теперь ссылаются на users.id")

def downgrade(cursor):
    print("🔄 Откат: Удаление внешних ключей и возврат структуры")
    
    # Удаляем внешние ключи
    foreign_keys = [
        ('events', 'fk_events_user_id'),
        ('notes', 'fk_notes_user_id'),
        ('project_members', 'fk_project_members_user_id'),
        ('projects', 'fk_projects_owner_id'),
        ('purchases', 'fk_purchases_user_id'),
        ('reminder_logs', 'fk_reminder_logs_user_id'),
        ('shopping', 'fk_shopping_user_id'),
        ('shopping_lists', 'fk_shopping_lists_user_id'),
        ('tasks', 'fk_tasks_user_id'),
        ('user_settings', 'fk_user_settings_user_id')
    ]
    
    for table_name, constraint_name in foreign_keys:
        cursor.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name}")
    
    print("⚠️  Для полного отката используйте резервную копию")