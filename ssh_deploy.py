#!/usr/bin/env python3
"""
🔐 SSH деплой скрипт для NetAngels
Подключается к серверу и выполняет миграции
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

def upload_migration_script():
    """Загрузить скрипт миграции на сервер"""
    print("📤 Загружаем скрипт миграции на сервер...")
    
    # Путь к локальному файлу
    local_script = Path(__file__).parent / 'server_migrate.py'
    
    # Команда scp для загрузки
    scp_command = [
        'scp',
        '-o', 'StrictHostKeyChecking=no',
        str(local_script),
        f"{SSH_CONFIG['user']}@{SSH_CONFIG['host']}:~/server_migrate.py"
    ]
    
    try:
        result = subprocess.run(scp_command, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Скрипт миграции загружен на сервер")
            return True
        else:
            print(f"❌ Ошибка загрузки: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Таймаут при загрузке файла")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def run_ssh_command(command):
    """Выполнить команду на сервере через SSH"""
    ssh_command = [
        'ssh',
        '-o', 'StrictHostKeyChecking=no',
        f"{SSH_CONFIG['user']}@{SSH_CONFIG['host']}",
        command
    ]
    
    try:
        result = subprocess.run(ssh_command, capture_output=True, text=True, timeout=60)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Таймаут выполнения команды"
    except Exception as e:
        return -1, "", str(e)

def check_python_on_server():
    """Проверить наличие Python на сервере"""
    print("🐍 Проверяем Python на сервере...")
    
    # Проверяем python3
    code, stdout, stderr = run_ssh_command('python3 --version')
    if code == 0:
        print(f"✅ Python найден: {stdout.strip()}")
        return 'python3'
    
    # Проверяем python
    code, stdout, stderr = run_ssh_command('python --version')
    if code == 0:
        print(f"✅ Python найден: {stdout.strip()}")
        return 'python'
    
    print("❌ Python не найден на сервере")
    return None

def install_dependencies():
    """Установить зависимости на сервере"""
    print("📦 Устанавливаем зависимости...")
    
    # Проверяем pip
    python_cmd = check_python_on_server()
    if not python_cmd:
        return False
    
    pip_cmd = 'pip3' if python_cmd == 'python3' else 'pip'
    
    # Устанавливаем psycopg2 (пробуем разные способы)
    code, stdout, stderr = run_ssh_command(f'{pip_cmd} install --user psycopg2-binary')
    if code == 0:
        print("✅ psycopg2 установлен")
    else:
        print(f"⚠️ Ошибка установки через pip: {stderr}")
        # Пробуем с --break-system-packages
        print("🔄 Пробуем установить с --break-system-packages...")
        code, stdout, stderr = run_ssh_command(f'{pip_cmd} install --user --break-system-packages psycopg2-binary')
        if code == 0:
            print("✅ psycopg2 установлен с --break-system-packages")
        else:
            print(f"⚠️ Не удалось установить psycopg2: {stderr}")
            print("ℹ️ Попробуем продолжить без установки...")
    
    return True

def run_migrations():
    """Выполнить миграции на сервере"""
    print("🔄 Выполняем миграции на сервере...")
    
    python_cmd = check_python_on_server()
    if not python_cmd:
        return False
    
    # Сначала проверяем статус
    print("\n📊 Проверяем статус миграций...")
    code, stdout, stderr = run_ssh_command(f'{python_cmd} ~/server_migrate.py status')
    
    if code == 0:
        print("Статус миграций:")
        print(stdout)
    else:
        print(f"⚠️ Ошибка проверки статуса: {stderr}")
    
    # Выполняем миграции
    print("\n🚀 Запускаем миграции...")
    code, stdout, stderr = run_ssh_command(f'{python_cmd} ~/server_migrate.py migrate')
    
    if code == 0:
        print("✅ Миграции выполнены успешно!")
        print(stdout)
        return True
    else:
        print(f"❌ Ошибка выполнения миграций: {stderr}")
        print(f"Вывод: {stdout}")
        return False

def cleanup_server():
    """Очистить временные файлы на сервере"""
    print("🧹 Очищаем временные файлы...")
    
    code, stdout, stderr = run_ssh_command('rm -f ~/server_migrate.py')
    if code == 0:
        print("✅ Временные файлы удалены")
    else:
        print(f"⚠️ Не удалось удалить временные файлы: {stderr}")

def check_database():
    """Проверить состояние БД на сервере"""
    print("📊 Проверяем состояние продакшн БД...")
    
    python_cmd = check_python_on_server()
    if not python_cmd:
        return False
    
    # Создаем временный скрипт для проверки БД
    check_script = '''
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": "postgres.c107597.h2",
    "database": "c107597_rptx_na4u_ru", 
    "user": "c107597_rptx_na4u_ru",
    "password": "ZiKceXoydixol93",
    "port": 5432
}

try:
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    
    with conn.cursor() as cur:
        print("🔗 Подключение к продакшн БД успешно!")
        
        # Список таблиц
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        tables = cur.fetchall()
        print(f"📋 Таблицы ({len(tables)} шт.): {[t['table_name'] for t in tables]}")
        
        # Миграции
        cur.execute("SELECT version, name FROM schema_migrations ORDER BY executed_at")
        migrations = cur.fetchall()
        print(f"🔄 Миграции ({len(migrations)} шт.):")
        for m in migrations:
            print(f"   ✅ {m['version']}: {m['name']}")
        
        # Количество записей
        tables_to_check = ["users", "projects", "tasks", "events", "shopping", "purchases"]
        print("📈 Записи:")
        for table in tables_to_check:
            try:
                cur.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cur.fetchone()["count"]
                print(f"   - {table}: {count}")
            except:
                print(f"   - {table}: ошибка")
    
    conn.close()
    print("✅ Проверка завершена!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
'''
    
    # Загружаем и выполняем скрипт
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(check_script)
        temp_file = f.name
    
    try:
        # Загружаем скрипт на сервер
        scp_command = [
            'scp', '-o', 'StrictHostKeyChecking=no',
            temp_file,
            f"{SSH_CONFIG['user']}@{SSH_CONFIG['host']}:~/check_db_temp.py"
        ]
        
        result = subprocess.run(scp_command, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"❌ Ошибка загрузки скрипта: {result.stderr}")
            return False
        
        # Выполняем скрипт
        code, stdout, stderr = run_ssh_command(f'{python_cmd} ~/check_db_temp.py')
        
        if code == 0:
            print(stdout)
            return True
        else:
            print(f"❌ Ошибка выполнения: {stderr}")
            return False
            
    finally:
        # Очищаем временные файлы
        os.unlink(temp_file)
        run_ssh_command('rm -f ~/check_db_temp.py')
    
    return False

def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SSH деплой и управление на NetAngels")
    parser.add_argument('command', choices=['deploy', 'check'], 
                       help='Команда: deploy - деплой миграций, check - проверка БД')
    
    args = parser.parse_args()
    
    print("🚀 SSH подключение к NetAngels")
    print(f"🔗 Подключение к {SSH_CONFIG['host']} как {SSH_CONFIG['user']}")
    
    # Проверяем наличие SSH
    try:
        subprocess.run(['ssh', '-V'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ SSH не найден. Установите OpenSSH client")
        sys.exit(1)
    
    try:
        if args.command == 'check':
            success = check_database()
            sys.exit(0 if success else 1)
        
        elif args.command == 'deploy':
            # 1. Загружаем скрипт миграции
            if not upload_migration_script():
                print("❌ Не удалось загрузить скрипт миграции")
                sys.exit(1)
            
            # 2. Устанавливаем зависимости
            if not install_dependencies():
                print("❌ Не удалось установить зависимости")
                sys.exit(1)
            
            # 3. Выполняем миграции
            if not run_migrations():
                print("❌ Миграции не выполнены")
                sys.exit(1)
            
            print("\n🎉 Деплой завершён успешно!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Операция прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)
    finally:
        # Очищаем временные файлы
        cleanup_server()

if __name__ == "__main__":
    main()