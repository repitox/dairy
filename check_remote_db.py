#!/usr/bin/env python3
"""
🔍 Скрипт для проверки структуры БД на NetAngels через Docker
Использует Docker контейнер для подключения к удаленной БД
"""

import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path

# Настройки БД NetAngels
DB_CONFIG = {
    'host': 'postgres.c107597.h2',
    'database': 'c107597_rptx_na4u_ru',
    'user': 'c107597_rptx_na4u_ru',
    'password': 'ZiKceXoydixol93',
    'port': 5432
}

def run_docker_command(python_script, timeout=120):
    """Выполнить Python скрипт в Docker контейнере через docker-compose"""
    try:
        # Создаем временный файл со скриптом в текущей директории
        temp_file = f'temp_check_{int(time.time())}.py'
        
        with open(temp_file, 'w') as f:
            f.write(python_script)
        
        # Выполняем скрипт в контейнере через docker-compose
        exec_result = subprocess.run(
            ['docker-compose', 'exec', 'app', 'python', temp_file],
            capture_output=True, text=True, timeout=timeout
        )
        
        return exec_result.returncode == 0, exec_result.stdout, exec_result.stderr
        
    except subprocess.TimeoutExpired:
        return False, "", f"Таймаут выполнения команды (>{timeout}s)"
    except Exception as e:
        return False, "", str(e)
    finally:
        # Удаляем временный файл
        if 'temp_file' in locals():
            try:
                os.unlink(temp_file)
            except:
                pass

def check_db_connection():
    """Проверить подключение к БД"""
    print("🔗 Проверяем подключение к БД NetAngels...")
    
    script = f'''
import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host='{DB_CONFIG["host"]}',
        database='{DB_CONFIG["database"]}',
        user='{DB_CONFIG["user"]}',
        password='{DB_CONFIG["password"]}',
        port={DB_CONFIG["port"]},
        connect_timeout=10
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ Подключение к БД NetAngels успешно")
    print(f"PostgreSQL версия: {{version[0]}}")
    
    cursor.execute("SELECT current_database();")
    db_name = cursor.fetchone()
    print(f"База данных: {{db_name[0]}}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Ошибка подключения к БД: {{e}}")
    sys.exit(1)
'''
    
    success, stdout, stderr = run_docker_command(script)
    if success:
        print(stdout)
        return True
    else:
        print(f"❌ Ошибка: {stderr}")
        return False

def get_table_structure():
    """Получить структуру таблиц БД"""
    print("\n📊 Получаем структуру таблиц...")
    
    script = f'''
import psycopg2
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(
        host='{DB_CONFIG["host"]}',
        database='{DB_CONFIG["database"]}',
        user='{DB_CONFIG["user"]}',
        password='{DB_CONFIG["password"]}',
        port={DB_CONFIG["port"]},
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
        print(f"  - {{table['table_name']}}")
    
    print(f"\\nВсего таблиц: {{len(tables)}}")
    
    # Получаем структуру каждой таблицы
    for table in tables:
        table_name = table['table_name']
        print(f"\\n🔍 Структура таблицы '{{table_name}}':")
        
        cursor.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable, 
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = cursor.fetchall()
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {{col['column_default']}}" if col['column_default'] else ""
            length = f"({{col['character_maximum_length']}})" if col['character_maximum_length'] else ""
            print(f"  {{col['column_name']}}: {{col['data_type']}}{{length}} {{nullable}}{{default}}")
        
        # Получаем количество записей
        cursor.execute(f"SELECT COUNT(*) FROM {{table_name}};")
        count = cursor.fetchone()['count']
        print(f"  📊 Записей в таблице: {{count}}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Ошибка получения структуры: {{e}}")
    import traceback
    traceback.print_exc()
'''
    
    success, stdout, stderr = run_docker_command(script)
    if success:
        print(stdout)
        return True
    else:
        print(f"❌ Ошибка: {stderr}")
        return False

def check_migrations_status():
    """Проверить статус миграций"""
    print("\n🔄 Проверяем статус миграций...")
    
    script = f'''
import psycopg2
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(
        host='{DB_CONFIG["host"]}',
        database='{DB_CONFIG["database"]}',
        user='{DB_CONFIG["user"]}',
        password='{DB_CONFIG["password"]}',
        port={DB_CONFIG["port"]},
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
            print(f"\\n📋 Выполненные миграции ({{len(migrations)}}):")
            for migration in migrations:
                print(f"  {{migration['version']}}: {{migration['name']}}")
                print(f"    Выполнено: {{migration['executed_at']}}")
        else:
            print("⚠️ Миграции не найдены")
    else:
        print("❌ Таблица schema_migrations не существует")
        print("Возможно, миграции еще не выполнялись")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Ошибка проверки миграций: {{e}}")
'''
    
    success, stdout, stderr = run_docker_command(script)
    if success:
        print(stdout)
        return True
    else:
        print(f"❌ Ошибка: {stderr}")
        return False

def check_indexes():
    """Проверить индексы БД"""
    print("\n🔍 Проверяем индексы...")
    
    script = f'''
import psycopg2
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(
        host='{DB_CONFIG["host"]}',
        database='{DB_CONFIG["database"]}',
        user='{DB_CONFIG["user"]}',
        password='{DB_CONFIG["password"]}',
        port={DB_CONFIG["port"]},
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
    
    print(f"📋 Найденные индексы ({{len(indexes)}}):")
    current_table = None
    
    for idx in indexes:
        if current_table != idx['tablename']:
            current_table = idx['tablename']
            print(f"\\n🔍 Таблица: {{current_table}}")
        
        print(f"  - {{idx['indexname']}}")
        # Показываем только тип индекса, не всю команду CREATE
        if 'UNIQUE' in idx['indexdef']:
            print(f"    Тип: UNIQUE")
        elif 'PRIMARY KEY' in idx['indexdef']:
            print(f"    Тип: PRIMARY KEY")
        else:
            print(f"    Тип: INDEX")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Ошибка проверки индексов: {{e}}")
'''
    
    success, stdout, stderr = run_docker_command(script)
    if success:
        print(stdout)
        return True
    else:
        print(f"❌ Ошибка: {stderr}")
        return False

def compare_with_local():
    """Сравнить с локальной БД"""
    print("\n🔄 Сравниваем с локальной БД...")
    
    script = f'''
import psycopg2
from psycopg2.extras import RealDictCursor

def get_tables(config):
    """Получить список таблиц"""
    conn = psycopg2.connect(**config, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = [row['table_name'] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    return tables

try:
    # Конфигурация удаленной БД
    remote_config = {{
        'host': '{DB_CONFIG["host"]}',
        'database': '{DB_CONFIG["database"]}',
        'user': '{DB_CONFIG["user"]}',
        'password': '{DB_CONFIG["password"]}',
        'port': {DB_CONFIG["port"]}
    }}
    
    # Конфигурация локальной БД
    local_config = {{
        'host': 'db',
        'database': 'telegram_app',
        'user': 'postgres',
        'password': 'password',
        'port': 5432
    }}
    
    print("📊 Получаем список таблиц...")
    remote_tables = get_tables(remote_config)
    local_tables = get_tables(local_config)
    
    print(f"\\n📋 Сравнение таблиц:")
    print(f"  Удаленная БД: {{len(remote_tables)}} таблиц")
    print(f"  Локальная БД: {{len(local_tables)}} таблиц")
    
    # Таблицы только в удаленной БД
    remote_only = set(remote_tables) - set(local_tables)
    if remote_only:
        print(f"\\n🔴 Таблицы только в удаленной БД:")
        for table in sorted(remote_only):
            print(f"  - {{table}}")
    
    # Таблицы только в локальной БД
    local_only = set(local_tables) - set(remote_tables)
    if local_only:
        print(f"\\n🟡 Таблицы только в локальной БД:")
        for table in sorted(local_only):
            print(f"  - {{table}}")
    
    # Общие таблицы
    common = set(remote_tables) & set(local_tables)
    if common:
        print(f"\\n🟢 Общие таблицы ({{len(common)}}):")
        for table in sorted(common):
            print(f"  - {{table}}")
    
except Exception as e:
    print(f"❌ Ошибка сравнения: {{e}}")
    import traceback
    traceback.print_exc()
'''
    
    success, stdout, stderr = run_docker_command(script)
    if success:
        print(stdout)
        return True
    else:
        print(f"❌ Ошибка: {stderr}")
        return False

def main():
    """Главная функция"""
    print("🔍 Проверка структуры БД на NetAngels через Docker")
    print(f"🔗 Удаленная БД: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    
    # Проверяем наличие Docker
    try:
        subprocess.run(['docker', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker не найден. Установите Docker")
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
        
        # 5. Сравниваем с локальной БД
        if not compare_with_local():
            print("❌ Не удалось сравнить с локальной БД")
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