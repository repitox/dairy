#!/usr/bin/env python3
"""
Скрипт для проверки навигации на продакшене через SSH
"""

import subprocess
import sys
import os
import time

def run_ssh_command(command, timeout=30):
    """Выполнить команду на удаленном сервере через SSH"""
    try:
        # Используем sshpass для автоматической передачи пароля
        ssh_command = [
            'sshpass', '-p', 'YiKceHokjelen89',
            'ssh', '-o', 'StrictHostKeyChecking=no',
            'c107597@h60.netangels.ru',
            f'cd dialist.ru/app && {command}'
        ]
        
        print(f"🔗 Выполняем команду: {command}")
        
        result = subprocess.run(
            ssh_command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            print(f"❌ Ошибка команды: {result.stderr}")
            return None
            
        return result.stdout.strip()
        
    except subprocess.TimeoutExpired:
        print(f"⏰ Таймаут команды ({timeout}s)")
        return None
    except FileNotFoundError:
        print("❌ sshpass не найден. Устанавливаем...")
        # Попробуем установить sshpass
        try:
            subprocess.run(['brew', 'install', 'sshpass'], check=True)
            return run_ssh_command(command, timeout)
        except:
            print("❌ Не удалось установить sshpass")
            return None
    except Exception as e:
        print(f"❌ Ошибка SSH: {e}")
        return None

def check_project_structure():
    """Проверить структуру проекта"""
    print("📁 Проверяем структуру проекта...")
    
    command = "ls -la"
    return run_ssh_command(command)

def check_database_connection():
    """Проверить подключение к БД и таблицу навигации"""
    print("🗄️ Проверяем БД и таблицу navigation_items...")
    
    command = '''python3 -c "
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('.env')

try:
    # Подключение к БД
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'postgres.c107597.h2'),
        database=os.getenv('DB_NAME', 'c107597_dialist_ru'),
        user=os.getenv('DB_USER', 'c107597_dialist_ru'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', 5432)
    )
    
    cursor = conn.cursor()
    
    # Проверяем существование таблицы
    cursor.execute(\\\"\\\"\\\"
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'navigation_items'
        );
    \\\"\\\"\\\")
    table_exists = cursor.fetchone()[0]
    print(f'📋 Таблица navigation_items существует: {table_exists}')
    
    if table_exists:
        # Получаем все записи навигации
        cursor.execute(\\\"\\\"\\\"
            SELECT 
                id, title, url, icon, category, 
                sort_order, is_active, is_visible,
                parent_id, group_name
            FROM navigation_items 
            ORDER BY sort_order ASC, title ASC;
        \\\"\\\"\\\")
        rows = cursor.fetchall()
        
        print(f'📊 Всего записей в navigation_items: {len(rows)}')
        print('=' * 80)
        
        for row in rows:
            active_status = '✅' if row[6] else '❌'
            visible_status = '👁️' if row[7] else '🙈'
            print(f'ID: {row[0]:2} | {row[1]:20} | {row[2]:30} | {row[3]:3} | {active_status} {visible_status}')
        
        # Проверяем активные и видимые записи
        cursor.execute(\\\"\\\"\\\"
            SELECT COUNT(*) FROM navigation_items 
            WHERE is_active = true AND is_visible = true;
        \\\"\\\"\\\")
        active_count = cursor.fetchone()[0]
        print(f'\\n🟢 Активных и видимых записей: {active_count}')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Ошибка БД: {e}')
    import traceback
    traceback.print_exc()
"'''
    
    return run_ssh_command(command)

def check_api_navigation():
    """Проверить API навигации"""
    print("🌐 Проверяем API навигации...")
    
    command = '''curl -s -X GET "http://localhost:8000/api/navigation?category=main" -H "Content-Type: application/json"'''
    
    return run_ssh_command(command)

def check_server_status():
    """Проверить статус сервера"""
    print("🔍 Проверяем статус сервера...")
    
    command = "ps aux | grep python3 | grep -v grep"
    return run_ssh_command(command)

def check_logs():
    """Проверить логи"""
    print("📝 Проверяем логи...")
    
    command = "tail -n 30 nohup.out | grep -E '(navigation|Navigation|ERROR|❌|API)'"
    return run_ssh_command(command)

def main():
    print("🚀 Диагностика навигации на продакшене")
    print("=" * 60)
    
    # 1. Проверяем структуру проекта
    structure = check_project_structure()
    if structure:
        print("✅ Структура проекта:")
        print(structure[:500] + "..." if len(structure) > 500 else structure)
        print()
    
    # 2. Проверяем статус сервера
    status = check_server_status()
    if status:
        print("✅ Статус сервера:")
        print(status)
        print()
    
    # 3. Проверяем БД и навигацию
    db_check = check_database_connection()
    if db_check:
        print("✅ Проверка БД:")
        print(db_check)
        print()
    
    # 4. Проверяем API
    api_response = check_api_navigation()
    if api_response:
        print("✅ API навигации:")
        try:
            import json
            formatted = json.dumps(json.loads(api_response), indent=2, ensure_ascii=False)
            print(formatted)
        except:
            print(api_response)
        print()
    
    # 5. Проверяем логи
    logs = check_logs()
    if logs:
        print("📝 Логи:")
        print(logs)
        print()
    
    print("🏁 Диагностика завершена")

if __name__ == "__main__":
    main()