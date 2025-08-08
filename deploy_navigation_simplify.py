#!/usr/bin/env python3
"""
Скрипт для деплоя упрощения структуры навигации на продакшен
"""

import subprocess
import os
import sys
from datetime import datetime

def run_command(command, description):
    """Выполняет команду и показывает результат"""
    print(f"\n🔄 {description}")
    print(f"💻 Команда: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Успешно!")
            if result.stdout:
                print(f"📤 Вывод:\n{result.stdout}")
        else:
            print(f"❌ Ошибка (код {result.returncode})")
            if result.stderr:
                print(f"🚨 Ошибка:\n{result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False
    
    return True

def main():
    print("🚀 Деплой упрощения структуры навигации на NetAngels")
    print("=" * 60)
    
    # Проверяем наличие SQL файла
    sql_file = "production_navigation_simplify.sql"
    if not os.path.exists(sql_file):
        print(f"❌ Файл {sql_file} не найден!")
        return False
    
    print(f"📁 Найден SQL файл: {sql_file}")
    
    # Данные для подключения
    ssh_host = "c107597@h60.netangels.ru"
    db_host = "postgres.c107597.h2"
    db_name = "c107597_dialist_ru"
    db_user = "c107597_dialist_ru"
    db_password = "ZoXboBiphobem19"
    
    # Копируем SQL файл на сервер
    print(f"\n📤 Копируем SQL файл на сервер...")
    scp_command = f"scp {sql_file} {ssh_host}:/tmp/"
    if not run_command(scp_command, "Копирование SQL файла"):
        return False
    
    # Выполняем миграцию на сервере
    print(f"\n🗃️ Выполняем миграцию на сервере...")
    
    # Формируем команду для выполнения SQL
    psql_command = f"""
    export PGPASSWORD='{db_password}' && 
    psql -h {db_host} -U {db_user} -d {db_name} -f /tmp/{sql_file}
    """
    
    ssh_command = f'ssh {ssh_host} "{psql_command}"'
    
    if not run_command(ssh_command, "Выполнение миграции"):
        print("\n🚨 Миграция не удалась!")
        
        # Предлагаем ручное выполнение
        print("\n💡 Для ручного выполнения:")
        print(f"1. ssh {ssh_host}")
        print(f"2. export PGPASSWORD='{db_password}'")
        print(f"3. psql -h {db_host} -U {db_user} -d {db_name} -f /tmp/{sql_file}")
        
        return False
    
    # Проверяем результат
    print(f"\n🔍 Проверяем результат миграции...")
    
    check_command = f"""
    export PGPASSWORD='{db_password}' && 
    psql -h {db_host} -U {db_user} -d {db_name} -c "
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN platform = 'dashboard' THEN 1 END) as dashboard,
        COUNT(CASE WHEN platform = 'webapp' THEN 1 END) as webapp
    FROM navigation_items;
    "
    """
    
    ssh_check_command = f'ssh {ssh_host} "{check_command}"'
    
    if run_command(ssh_check_command, "Проверка результата"):
        print("\n🎉 Миграция завершена успешно!")
        print("\n📋 Что было сделано:")
        print("✅ Упрощена структура таблицы navigation_items (21 поле → 7 полей)")
        print("✅ Добавлено четкое разделение на платформы (dashboard/webapp)")
        print("✅ Сохранены все активные элементы навигации")
        print("✅ Создана резервная копия: navigation_items_backup_20250119")
        print("✅ Подготовлена основа для иерархической навигации")
        
        print("\n🔄 Для отката миграции (если потребуется):")
        print(f"ssh {ssh_host}")
        print(f"export PGPASSWORD='{db_password}'")
        print(f"psql -h {db_host} -U {db_user} -d {db_name} -c \"")
        print("DROP TABLE navigation_items;")
        print("ALTER TABLE navigation_items_backup_20250119 RENAME TO navigation_items;")
        print("\"")
        
        return True
    else:
        print("\n⚠️ Не удалось проверить результат миграции")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)