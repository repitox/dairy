#!/usr/bin/env python3
"""
Скрипт для исправления ограничений таблицы project_members
Добавляет уникальное ограничение на (project_id, user_id)
"""
import psycopg2
import os

def fix_project_members_constraint():
    """Исправляет ограничения таблицы project_members"""
    
    # Продакшн DATABASE_URL
    DATABASE_URL = "postgresql://c107597_dialist_ru:ZoXboBiphobem19@postgres.c107597.h2:5432/c107597_dialist_ru"
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("🔍 Проверяем текущие ограничения таблицы project_members...")
        
        # Проверяем существующие ограничения
        cur.execute("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'project_members'
        """)
        
        constraints = cur.fetchall()
        print("Текущие ограничения:")
        for constraint in constraints:
            print(f"  {constraint[0]} - {constraint[1]}")
        
        # Проверяем, есть ли уже уникальное ограничение на (project_id, user_id)
        cur.execute("""
            SELECT tc.constraint_name 
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'project_members' 
                AND tc.constraint_type = 'UNIQUE'
                AND kcu.column_name IN ('project_id', 'user_id')
            GROUP BY tc.constraint_name
            HAVING COUNT(*) = 2
        """)
        
        unique_constraint = cur.fetchone()
        
        if unique_constraint:
            print(f"✅ Уникальное ограничение уже существует: {unique_constraint[0]}")
        else:
            print("❌ Уникальное ограничение на (project_id, user_id) отсутствует")
            
            # Сначала удаляем дубликаты, если они есть
            print("🧹 Удаляем возможные дубликаты...")
            cur.execute("""
                DELETE FROM project_members 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM project_members 
                    GROUP BY project_id, user_id
                )
            """)
            deleted_count = cur.rowcount
            print(f"🗑️ Удалено дубликатов: {deleted_count}")
            
            # Добавляем уникальное ограничение
            print("➕ Добавляем уникальное ограничение...")
            cur.execute("""
                ALTER TABLE project_members 
                ADD CONSTRAINT unique_project_user 
                UNIQUE (project_id, user_id)
            """)
            print("✅ Уникальное ограничение добавлено")
        
        # Проверяем структуру таблицы
        cur.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'project_members' 
            ORDER BY ordinal_position
        """)
        
        print("\nСтруктура таблицы project_members:")
        columns = cur.fetchall()
        for column in columns:
            print(f"  {column[0]} - {column[1]} - nullable: {column[2]}")
        
        # Сохраняем изменения
        conn.commit()
        print("\n✅ Все изменения сохранены")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fix_project_members_constraint()