#!/usr/bin/env python3
"""
Скрипт для деплоя исправлений списков покупок на продакшн сервер NetAngels
"""

import subprocess
import sys
import os

def run_ssh_command(command):
    """Выполнить команду на SSH сервере"""
    ssh_command = f'ssh c107597@h60.netangels.ru "cd dialist.ru/app && {command}"'
    print(f"🔧 Выполняем: {command}")
    
    try:
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Успешно: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Ошибка: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False

def deploy_shopping_fix():
    """Основная функция деплоя"""
    print("🚀 Деплой исправлений списков покупок на NetAngels...")
    
    # 1. Проверяем подключение
    print("\n1️⃣ Проверяем подключение к серверу...")
    if not run_ssh_command("pwd"):
        print("❌ Не удалось подключиться к серверу")
        return False
    
    # 2. Проверяем текущее состояние миграций
    print("\n2️⃣ Проверяем статус миграций...")
    run_ssh_command("python3 server_migrate.py status")
    
    # 3. Проверяем структуру таблицы purchases
    print("\n3️⃣ Проверяем структуру таблицы purchases...")
    check_command = '''python3 -c "
from db import get_conn
try:
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Проверяем поля таблицы
            cur.execute(\\\"SELECT column_name FROM information_schema.columns WHERE table_name = 'purchases' ORDER BY ordinal_position;\\\")
            columns = [row[0] for row in cur.fetchall()]
            print(f'Поля таблицы purchases: {columns}')
            
            # Проверяем последовательность
            cur.execute(\\\"SELECT EXISTS (SELECT 1 FROM pg_sequences WHERE sequencename = 'purchases_id_seq');\\\")
            seq_exists = cur.fetchone()[0]
            print(f'Последовательность purchases_id_seq: {\\\"есть\\\" if seq_exists else \\\"нет\\\"}')
            
            # Проверяем количество записей
            cur.execute('SELECT COUNT(*) FROM purchases;')
            count = cur.fetchone()[0]
            print(f'Количество записей: {count}')
            
except Exception as e:
    print(f'Ошибка проверки: {e}')
"'''
    run_ssh_command(check_command)
    
    # 4. Выполняем миграции
    print("\n4️⃣ Выполняем миграции...")
    if run_ssh_command("python3 server_migrate.py migrate"):
        print("✅ Миграции выполнены успешно")
    else:
        print("❌ Ошибка выполнения миграций")
        
        # Попробуем исправить таблицу вручную
        print("\n🔧 Попытка исправления таблицы purchases вручную...")
        fix_command = '''python3 -c "
from db import get_conn
try:
    with get_conn() as conn:
        with conn.cursor() as cur:
            print('Исправляем таблицу purchases...')
            
            # Создаем последовательность если её нет
            cur.execute(\\\"CREATE SEQUENCE IF NOT EXISTS purchases_id_seq;\\\")
            cur.execute(\\\"SELECT setval('purchases_id_seq', COALESCE((SELECT MAX(id) FROM purchases), 0) + 1, false);\\\")
            cur.execute(\\\"ALTER TABLE purchases ALTER COLUMN id SET DEFAULT nextval('purchases_id_seq');\\\")
            cur.execute(\\\"ALTER SEQUENCE purchases_id_seq OWNED BY purchases.id;\\\")
            
            # Добавляем недостающие поля
            cur.execute(\\\"ALTER TABLE purchases ADD COLUMN IF NOT EXISTS shopping_list_id INTEGER;\\\")
            cur.execute(\\\"ALTER TABLE purchases ADD COLUMN IF NOT EXISTS url TEXT;\\\")
            cur.execute(\\\"ALTER TABLE purchases ADD COLUMN IF NOT EXISTS comment TEXT;\\\")
            
            # Создаем индекс
            cur.execute(\\\"CREATE INDEX IF NOT EXISTS idx_purchases_shopping_list_id ON purchases(shopping_list_id);\\\")
            
            conn.commit()
            print('✅ Таблица purchases исправлена')
            
except Exception as e:
    print(f'❌ Ошибка исправления: {e}')
    import traceback
    traceback.print_exc()
"'''
        run_ssh_command(fix_command)
    
    # 5. Проверяем финальное состояние
    print("\n5️⃣ Проверяем финальное состояние...")
    run_ssh_command("python3 server_migrate.py status")
    
    # 6. Тестируем API
    print("\n6️⃣ Тестируем API...")
    test_command = '''python3 -c "
import requests
import json

try:
    # Проверяем получение списков покупок
    response = requests.get('http://localhost:8000/api/shopping-lists?user_id=2')
    if response.status_code == 200:
        lists = response.json()
        print(f'✅ API списков работает: найдено {len(lists)} списков')
        
        if lists:
            # Пробуем создать товар
            list_id = lists[0]['id']
            data = {
                'user_id': 2,
                'name': 'Тестовый товар',
                'quantity': 1,
                'shopping_list_id': list_id,
                'comment': 'Тест после миграции'
            }
            
            response = requests.post('http://localhost:8000/api/shopping', json=data)
            if response.status_code == 200:
                result = response.json()
                print(f'✅ Создание товара работает: ID {result.get(\\\"id\\\")}')
            else:
                print(f'❌ Ошибка создания товара: {response.status_code} - {response.text}')
        else:
            print('⚠️ Нет списков покупок для тестирования')
    else:
        print(f'❌ API списков не работает: {response.status_code}')
        
except Exception as e:
    print(f'❌ Ошибка тестирования API: {e}')
"'''
    run_ssh_command(test_command)
    
    print("\n🎉 Деплой завершен!")
    return True

if __name__ == "__main__":
    deploy_shopping_fix()