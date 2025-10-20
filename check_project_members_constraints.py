#!/usr/bin/env python3
"""
Скрипт для проверки ограничений таблицы project_members на продакшене
"""
import psycopg2
import os

# Используем продакшн DATABASE_URL
DATABASE_URL = "postgresql://c107597_dialist_ru:ZoXboBiphobem19@postgres.c107597.h2:5432/c107597_dialist_ru"

def check_constraints():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Проверяем ограничения таблицы project_members
        cur.execute("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'project_members'
        """)
        
        print("Ограничения таблицы project_members:")
        constraints = cur.fetchall()
        for constraint in constraints:
            print(f"  {constraint[0]} - {constraint[1]}")
        
        # Проверяем индексы
        cur.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'project_members'
        """)
        
        print("\nИндексы таблицы project_members:")
        indexes = cur.fetchall()
        for index in indexes:
            print(f"  {index[0]}: {index[1]}")
        
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
        
        conn.close()
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    check_constraints()