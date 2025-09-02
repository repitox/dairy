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
        # Если есть temp_user_id, сначала проверим и наполним данные
        # На шаге 2 мы уже ставили значения, но перепроверим, чтобы не оставить NULL
        cursor.execute(f"""
            UPDATE {table_name} t
            SET temp_user_id = u.id
            FROM users u
            WHERE t.temp_user_id IS NULL
              AND (
                    (EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='user_id') AND t.{column_name} = u.user_id)
                 OR (EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='telegram_id') AND t.{column_name} = u.telegram_id)
              )
        """)

        # Пытаемся удалить старую колонку, если она существует
        cursor.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND column_name = '{column_name}'
                ) THEN
                    ALTER TABLE {table_name} DROP COLUMN {column_name};
                END IF;
            END $$;
        """)
        
        # Переименовываем временную колонку, только если она есть и целевой колонки уже нет
        cursor.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND column_name = 'temp_user_id'
                ) AND NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND column_name = '{column_name}'
                ) THEN
                    ALTER TABLE {table_name} RENAME COLUMN temp_user_id TO {column_name};
                END IF;
            END $$;
        """)

        # Добавляем NOT NULL только если нет NULL-значений
        cursor.execute(f"SELECT COUNT(*) AS cnt FROM {table_name} WHERE {column_name} IS NULL")
        row = cursor.fetchone()
        nulls = row['cnt'] if isinstance(row, dict) else (row[0] if row else 0)
        if nulls == 0:
            cursor.execute(f"ALTER TABLE {table_name} ALTER COLUMN {column_name} SET NOT NULL")
        
        print(f"✅ Колонка {column_name} обновлена в таблице {table_name}")
    
    print("✅ Все колонки переключены на новые значения")

# Совместимость с MigrationManager

def up(cursor):
    return upgrade(cursor)


def down(cursor):
    return downgrade(cursor)

def downgrade(cursor):
    print("🔄 Откат: Возврат к старым колонкам")
    
    # Откат сложный, поэтому лучше использовать резервную копию
    print("⚠️  Откат этого этапа требует восстановления из резервной копии")
    print("⚠️  Используйте резервную копию для восстановления")