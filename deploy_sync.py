#!/usr/bin/env python3
"""
🚀 Универсальный скрипт синхронизации БД между локальной разработкой и продакшн
Использует систему миграций для безопасного обновления схемы БД
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from migrations.migration_manager import MigrationManager

# Загружаем переменные окружения
load_dotenv()

def get_local_database_url():
    """Получить URL локальной БД (Docker)"""
    # Если запускаем внутри Docker контейнера, используем имя сервиса
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    # Если запускаем снаружи Docker, используем localhost
    return "postgresql://postgres:password@localhost:5432/telegram_app"

def get_production_database_url():
    """Получить URL продакшн БД (NetAngels)"""
    return "postgresql://c107597_rptx_na4u_ru:ZiKceXoydixol93@postgres.c107597.h2:5432/c107597_rptx_na4u_ru"

def sync_local_to_production():
    """Синхронизировать локальную БД с продакшн"""
    print("🔄 Синхронизация локальной БД с продакшн...")
    
    # Сначала проверяем локальную БД
    print("\n📋 Проверка локальной БД:")
    local_manager = MigrationManager(get_local_database_url())
    local_manager.status()
    
    # Применяем миграции к локальной БД если нужно
    local_pending = local_manager.get_pending_migrations()
    if local_pending:
        print(f"\n🔄 Применяем {len(local_pending)} миграций к локальной БД...")
        if not local_manager.migrate():
            print("❌ Не удалось применить миграции к локальной БД")
            return False
    
    # Теперь работаем с продакшн БД
    print("\n📋 Проверка продакшн БД:")
    prod_manager = MigrationManager(get_production_database_url())
    prod_manager.status()
    
    # Применяем миграции к продакшн БД
    prod_pending = prod_manager.get_pending_migrations()
    if prod_pending:
        print(f"\n🔄 Применяем {len(prod_pending)} миграций к продакшн БД...")
        if not prod_manager.migrate():
            print("❌ Не удалось применить миграции к продакшн БД")
            return False
    else:
        print("✅ Продакшн БД уже синхронизирована")
    
    print("\n🎉 Синхронизация завершена успешно!")
    return True

def check_status():
    """Проверить статус обеих БД"""
    print("📊 Статус локальной БД (Docker):")
    try:
        local_manager = MigrationManager(get_local_database_url())
        local_manager.status()
    except Exception as e:
        print(f"❌ Ошибка подключения к локальной БД: {e}")
    
    print("\n📊 Статус продакшн БД (NetAngels):")
    try:
        prod_manager = MigrationManager(get_production_database_url())
        prod_manager.status()
    except Exception as e:
        print(f"❌ Ошибка подключения к продакшн БД: {e}")

def create_migration_template(name: str):
    """Создать шаблон новой миграции"""
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{name}.py"
    filepath = os.path.join("migrations", "scripts", filename)
    
    template = f'''"""
{name.replace('_', ' ').title()}
"""

def up(cursor):
    """Применить миграцию"""
    
    # Ваш код миграции здесь
    # Например:
    # cursor.execute("ALTER TABLE users ADD COLUMN new_field TEXT;")
    
    print("✅ Миграция {name} применена")


def down(cursor):
    """Откатить миграцию"""
    
    # Код для отката миграции
    # Например:
    # cursor.execute("ALTER TABLE users DROP COLUMN new_field;")
    
    print("✅ Миграция {name} откачена")
'''
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"✅ Создан шаблон миграции: {filepath}")
    print("📝 Отредактируйте файл и добавьте необходимые изменения БД")

def dump_schemas():
    """Создать дампы схем обеих БД для сравнения"""
    print("📄 Создание дампов схем...")
    
    try:
        local_manager = MigrationManager(get_local_database_url())
        local_dump = local_manager.create_schema_dump("local_schema.sql")
        if local_dump:
            print(f"✅ Дамп локальной БД: {local_dump}")
    except Exception as e:
        print(f"❌ Ошибка создания дампа локальной БД: {e}")
    
    try:
        prod_manager = MigrationManager(get_production_database_url())
        prod_dump = prod_manager.create_schema_dump("production_schema.sql")
        if prod_dump:
            print(f"✅ Дамп продакшн БД: {prod_dump}")
    except Exception as e:
        print(f"❌ Ошибка создания дампа продакшн БД: {e}")

def main():
    parser = argparse.ArgumentParser(description="Синхронизация БД между локальной разработкой и продакшн")
    parser.add_argument('command', choices=['sync', 'status', 'create', 'dump'], 
                       help='Команда для выполнения')
    parser.add_argument('--name', help='Имя новой миграции (для команды create)')
    
    args = parser.parse_args()
    
    if args.command == 'sync':
        success = sync_local_to_production()
        sys.exit(0 if success else 1)
    
    elif args.command == 'status':
        check_status()
    
    elif args.command == 'create':
        if not args.name:
            print("❌ Укажите имя миграции: --name my_migration_name")
            sys.exit(1)
        create_migration_template(args.name)
    
    elif args.command == 'dump':
        dump_schemas()

if __name__ == "__main__":
    main()