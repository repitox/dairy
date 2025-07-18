#!/usr/bin/env python3
"""
🔍 Скрипт для проверки структуры БД на NetAngels
Подключается к серверу и проверяет таблицы, индексы и данные
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

# Настройки SSH
SSH_CONFIG = {
    'host': 'h60.netangels.ru',
    'user': 'c107597',
    'password': 'YiKceHokjelen89'
}

def run_ssh_command(command, timeout=60):
    """Выполнить команду на сервере через SSH"""
    ssh_command = [
        'ssh',
        '-o', 'StrictHostKeyChecking=no',
        f"{SSH_CONFIG['user']}@{SSH_CONFIG['host']}",
        command
    ]
    
    try:
        result = subprocess.run(ssh_command, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Таймаут выполнения команды (>{timeout}s)"
    except Exception as e:
        return -1, "", str(e)

def check_db_connection():
    """Проверить подключение к БД"""
    print("🔗 Проверяем подключение к БД...")
    
    # Создаем временный Python скрипт для проверки подключения
    db_check_script = '''
import psycopg2
try:
    conn = psycopg2.connect(
        host='postgres.c107597.h2',
        database='c107597_rptx_na4u_ru',
        user='c107597_rptx_na4u_ru',
        password='ZiKceXoydixol93',
        port=5432
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ Подключение к БД успешно")
    print(f"PostgreSQL версия: {version[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Ошибка подключения к БД: {e}")
    exit(1)
'''
    
    # Записываем скрипт во временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(db_check_script)
        temp_file = f.name
    
    try:
        # Загружаем скрипт на сервер
        upload_cmd = [
            'scp', '-o', 'StrictHostKeyChecking=no',
            temp_file, 
            f"{SSH_CONFIG['user']}@{SSH_CONFIG['host']}:~/db_check.py"
        ]
        
        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Ошибка загрузки скрипта: {result.stderr}")
            return False
        
        # Выполняем скрипт на сервере
        code, stdout, stderr = run_ssh_command("python3 ~/db_check.py")
        
        if code == 0:
            print(stdout)
            return True
        else:
            print(f"❌ Ошибка выполнения: {stderr}")
            return False
            
    finally:
        # Удаляем временный файл локально
        os.unlink(temp_file)
        # Удаляем файл на сервере
        run_ssh_command("rm -f ~/db_check.py")

def get_table_structure():
    """Получить структуру таблиц БД"""
    print("\n📊 Получаем структуру таблиц...")
    
    # Создаем скрипт для получения структуры таблиц
    structure_script = '''
import psycopg2
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(
        host='postgres.c107597.h2',
        database='c107597_rptx_na4u_ru',
        user='c107597_rptx_na4u_ru',
        password='ZiKceXoydixol93',
        port=5432,
        cursor_factory=RealDictCursor
    )
    cursor = conn.cursor()
    
    # Получаем список таблиц
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    print("📋 Найденные таблицы:")
    for table in tables:
        print(f"  - {table['table_name']}")
    
    print(f"\\nВсего таблиц: {len(tables)}")
    
    # Получаем структуру каждой таблицы
    for table in tables:
        table_name = table['table_name']
        print(f"\\n🔍 Структура таблицы '{table_name}':")
        
        cursor.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable, 
                column_default
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = cursor.fetchall()
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        # Получаем количество записей
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()['count']
        print(f"  📊 Записей в таблице: {count}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Ошибка получения структуры: {e}")
    exit(1)
'''
    
    # Записываем скрипт во временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(structure_script)
        temp_file = f.name
    
    try:
        # Загружаем скрипт на сервер
        upload_cmd = [
            'scp', '-o', 'StrictHostKeyChecking=no',
            temp_file, 
            f"{SSH_CONFIG['user']}@{SSH_CONFIG['host']}:~/structure_check.py"
        ]
        
        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Ошибка загрузки скрипта: {result.stderr}")
            return False
        
        # Выполняем скрипт на сервере
        code, stdout, stderr = run_ssh_command("python3 ~/structure_check.py", timeout=120)
        
        if code == 0:
            print(stdout)
            return True
        else:
            print(f"❌ Ошибка выполнения: {stderr}")
            return False
            
    finally:
        # Удаляем временный файл локально
        os.unlink(temp_file)
        # Удаляем файл на сервере
        run_ssh_command("rm -f ~/structure_check.py")

def check_migrations_status():
    """Проверить статус миграций"""
    print("\n🔄 Проверяем статус миграций...")
    
    # Создаем скрипт для проверки миграций
    migration_script = '''
import psycopg2
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(
        host='postgres.c107597.h2',
        database='c107597_rptx_na4u_ru',
        user='c107597_rptx_na4u_ru',
        password='ZiKceXoydixol93',
        port=5432,
        cursor_factory=RealDictCursor
    )
    cursor = conn.cursor()
    
    # Проверяем наличие таблицы миграций
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'schema_migrations'
        );
    """)
    
    migrations_table_exists = cursor.fetchone()['exists']
    
    if migrations_table_exists:
        print("✅ Таблица schema_migrations существует")
        
        # Получаем список выполненных миграций
        cursor.execute("""
            SELECT version, name, executed_at 
            FROM schema_migrations 
            ORDER BY version;
        """)
        
        migrations = cursor.fetchall()
        if migrations:
            print(f"\\n📋 Выполненные миграции ({len(migrations)}):")
            for migration in migrations:
                print(f"  {migration['version']}: {migration['name']}")
                print(f"    Выполнено: {migration['executed_at']}")
        else:
            print("⚠️ Миграции не найдены")
    else:
        print("❌ Таблица schema_migrations не существует")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Ошибка проверки миграций: {e}")
    exit(1)
'''
    
    # Записываем скрипт во временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(migration_script)
        temp_file = f.name
    
    try:
        # Загружаем скрипт на сервер
        upload_cmd = [
            'scp', '-o', 'StrictHostKeyChecking=no',
            temp_file, 
            f"{SSH_CONFIG['user']}@{SSH_CONFIG['host']}:~/migration_check.py"
        ]
        
        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Ошибка загрузки скрипта: {result.stderr}")
            return False
        
        # Выполняем скрипт на сервере
        code, stdout, stderr = run_ssh_command("python3 ~/migration_check.py")
        
        if code == 0:
            print(stdout)
            return True
        else:
            print(f"❌ Ошибка выполнения: {stderr}")
            return False
            
    finally:
        # Удаляем временный файл локально
        os.unlink(temp_file)
        # Удаляем файл на сервере
        run_ssh_command("rm -f ~/migration_check.py")

def check_indexes():
    """Проверить индексы БД"""
    print("\n🔍 Проверяем индексы...")
    
    # Создаем скрипт для проверки индексов
    index_script = '''
import psycopg2
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(
        host='postgres.c107597.h2',
        database='c107597_rptx_na4u_ru',
        user='c107597_rptx_na4u_ru',
        password='ZiKceXoydixol93',
        port=5432,
        cursor_factory=RealDictCursor
    )
    cursor = conn.cursor()
    
    # Получаем список индексов
    cursor.execute("""
        SELECT 
            schemaname,
            tablename,
            indexname,
            indexdef
        FROM pg_indexes 
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname;
    """)
    
    indexes = cursor.fetchall()
    
    print(f"📋 Найденные индексы ({len(indexes)}):")
    current_table = None
    
    for idx in indexes:
        if current_table != idx['tablename']:
            current_table = idx['tablename']
            print(f"\\n🔍 Таблица: {current_table}")
        
        print(f"  - {idx['indexname']}")
        print(f"    {idx['indexdef']}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Ошибка проверки индексов: {e}")
    exit(1)
'''
    
    # Записываем скрипт во временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(index_script)
        temp_file = f.name
    
    try:
        # Загружаем скрипт на сервер
        upload_cmd = [
            'scp', '-o', 'StrictHostKeyChecking=no',
            temp_file, 
            f"{SSH_CONFIG['user']}@{SSH_CONFIG['host']}:~/index_check.py"
        ]
        
        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Ошибка загрузки скрипта: {result.stderr}")
            return False
        
        # Выполняем скрипт на сервере
        code, stdout, stderr = run_ssh_command("python3 ~/index_check.py")
        
        if code == 0:
            print(stdout)
            return True
        else:
            print(f"❌ Ошибка выполнения: {stderr}")
            return False
            
    finally:
        # Удаляем временный файл локально
        os.unlink(temp_file)
        # Удаляем файл на сервере
        run_ssh_command("rm -f ~/index_check.py")

def main():
    """Главная функция"""
    print("🔍 Проверка структуры БД на NetAngels")
    print(f"🔗 Подключение к {SSH_CONFIG['host']} как {SSH_CONFIG['user']}")
    
    # Проверяем наличие SSH
    try:
        subprocess.run(['ssh', '-V'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ SSH не найден. Установите OpenSSH client")
        sys.exit(1)
    
    try:
        # 1. Проверяем подключение к БД
        if not check_db_connection():
            print("❌ Не удалось подключиться к БД")
            sys.exit(1)
        
        # 2. Получаем структуру таблиц
        if not get_table_structure():
            print("❌ Не удалось получить структуру таблиц")
            sys.exit(1)
        
        # 3. Проверяем статус миграций
        if not check_migrations_status():
            print("❌ Не удалось проверить миграции")
            sys.exit(1)
        
        # 4. Проверяем индексы
        if not check_indexes():
            print("❌ Не удалось проверить индексы")
            sys.exit(1)
        
        print("\n🎉 Проверка завершена успешно!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Проверка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()