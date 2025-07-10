#!/usr/bin/env python3
"""
🔄 Универсальный менеджер миграций
Система для управления миграциями базы данных между локальной разработкой и продакшн
"""

import os
import sys
import importlib.util
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Any
import glob

class MigrationManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.migrations_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        self.ensure_migrations_table()
    
    def get_conn(self):
        """Получить подключение к БД"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def ensure_migrations_table(self):
        """Создать таблицу для отслеживания миграций"""
        try:
            with self.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS schema_migrations (
                            id SERIAL PRIMARY KEY,
                            version VARCHAR(255) UNIQUE NOT NULL,
                            name TEXT NOT NULL,
                            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            checksum TEXT
                        );
                    """)
                    conn.commit()
        except Exception as e:
            print(f"❌ Ошибка создания таблицы миграций: {e}")
            raise
    
    def get_executed_migrations(self) -> List[str]:
        """Получить список выполненных миграций"""
        try:
            with self.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT version FROM schema_migrations ORDER BY version")
                    return [row['version'] for row in cur.fetchall()]
        except Exception as e:
            print(f"❌ Ошибка получения списка миграций: {e}")
            return []
    
    def get_available_migrations(self) -> List[Dict[str, Any]]:
        """Получить список доступных миграций"""
        migrations = []
        pattern = os.path.join(self.migrations_dir, "*.py")
        
        for file_path in sorted(glob.glob(pattern)):
            filename = os.path.basename(file_path)
            if filename.startswith('__'):
                continue
                
            # Извлекаем версию из имени файла (формат: YYYYMMDD_HHMMSS_name.py)
            version = filename.split('_')[0] + '_' + filename.split('_')[1]
            name = '_'.join(filename.split('_')[2:]).replace('.py', '')
            
            migrations.append({
                'version': version,
                'name': name,
                'filename': filename,
                'path': file_path
            })
        
        return migrations
    
    def get_pending_migrations(self) -> List[Dict[str, Any]]:
        """Получить список неприменённых миграций"""
        executed = set(self.get_executed_migrations())
        available = self.get_available_migrations()
        
        return [m for m in available if m['version'] not in executed]
    
    def execute_migration(self, migration: Dict[str, Any]) -> bool:
        """Выполнить одну миграцию"""
        print(f"🔄 Выполняем миграцию: {migration['version']} - {migration['name']}")
        
        try:
            # Загружаем модуль миграции
            spec = importlib.util.spec_from_file_location(
                f"migration_{migration['version']}", 
                migration['path']
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Выполняем миграцию
            if hasattr(module, 'up'):
                with self.get_conn() as conn:
                    try:
                        # Выполняем миграцию в транзакции
                        with conn.cursor() as cur:
                            module.up(cur)
                            
                            # Записываем в таблицу миграций
                            cur.execute("""
                                INSERT INTO schema_migrations (version, name)
                                VALUES (%s, %s)
                            """, (migration['version'], migration['name']))
                            
                        conn.commit()
                        print(f"✅ Миграция {migration['version']} выполнена успешно")
                        return True
                        
                    except Exception as e:
                        conn.rollback()
                        print(f"❌ Ошибка выполнения миграции {migration['version']}: {e}")
                        return False
            else:
                print(f"❌ Миграция {migration['version']} не содержит функцию up()")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка загрузки миграции {migration['version']}: {e}")
            return False
    
    def rollback_migration(self, migration: Dict[str, Any]) -> bool:
        """Откатить миграцию"""
        print(f"🔄 Откатываем миграцию: {migration['version']} - {migration['name']}")
        
        try:
            # Загружаем модуль миграции
            spec = importlib.util.spec_from_file_location(
                f"migration_{migration['version']}", 
                migration['path']
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Откатываем миграцию
            if hasattr(module, 'down'):
                with self.get_conn() as conn:
                    try:
                        with conn.cursor() as cur:
                            module.down(cur)
                            
                            # Удаляем из таблицы миграций
                            cur.execute("""
                                DELETE FROM schema_migrations 
                                WHERE version = %s
                            """, (migration['version'],))
                            
                        conn.commit()
                        print(f"✅ Миграция {migration['version']} откачена успешно")
                        return True
                        
                    except Exception as e:
                        conn.rollback()
                        print(f"❌ Ошибка отката миграции {migration['version']}: {e}")
                        return False
            else:
                print(f"❌ Миграция {migration['version']} не содержит функцию down()")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка загрузки миграции {migration['version']}: {e}")
            return False
    
    def migrate(self) -> bool:
        """Выполнить все неприменённые миграции"""
        pending = self.get_pending_migrations()
        
        if not pending:
            print("✅ Все миграции уже применены")
            return True
        
        print(f"📋 Найдено {len(pending)} неприменённых миграций:")
        for migration in pending:
            print(f"   - {migration['version']}: {migration['name']}")
        
        success_count = 0
        for migration in pending:
            if self.execute_migration(migration):
                success_count += 1
            else:
                print(f"❌ Остановка на миграции {migration['version']}")
                break
        
        if success_count == len(pending):
            print(f"🎉 Все {success_count} миграций выполнены успешно!")
            return True
        else:
            print(f"⚠️ Выполнено {success_count} из {len(pending)} миграций")
            return False
    
    def status(self):
        """Показать статус миграций"""
        executed = set(self.get_executed_migrations())
        available = self.get_available_migrations()
        pending = self.get_pending_migrations()
        
        print("📊 Статус миграций:")
        print(f"   Всего доступно: {len(available)}")
        print(f"   Выполнено: {len(executed)}")
        print(f"   Ожидает выполнения: {len(pending)}")
        
        if pending:
            print("\n📋 Неприменённые миграции:")
            for migration in pending:
                print(f"   ❌ {migration['version']}: {migration['name']}")
        
        if available:
            print("\n📋 Все миграции:")
            for migration in available:
                status = "✅" if migration['version'] in executed else "❌"
                print(f"   {status} {migration['version']}: {migration['name']}")
    
    def create_schema_dump(self, output_file: str = None):
        """Создать дамп схемы БД"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"schema_dump_{timestamp}.sql"
        
        try:
            with self.get_conn() as conn:
                with conn.cursor() as cur:
                    # Получаем информацию о всех таблицах
                    cur.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        ORDER BY table_name
                    """)
                    tables = [row['table_name'] for row in cur.fetchall()]
                    
                    schema_sql = []
                    schema_sql.append("-- Дамп схемы базы данных")
                    schema_sql.append(f"-- Создан: {datetime.now().isoformat()}")
                    schema_sql.append("")
                    
                    for table in tables:
                        # Получаем DDL для каждой таблицы
                        cur.execute(f"""
                            SELECT column_name, data_type, is_nullable, column_default
                            FROM information_schema.columns
                            WHERE table_name = '{table}'
                            ORDER BY ordinal_position
                        """)
                        columns = cur.fetchall()
                        
                        schema_sql.append(f"-- Таблица: {table}")
                        schema_sql.append(f"CREATE TABLE IF NOT EXISTS {table} (")
                        
                        column_defs = []
                        for col in columns:
                            col_def = f"    {col['column_name']} {col['data_type']}"
                            if col['is_nullable'] == 'NO':
                                col_def += " NOT NULL"
                            if col['column_default']:
                                col_def += f" DEFAULT {col['column_default']}"
                            column_defs.append(col_def)
                        
                        schema_sql.append(",\n".join(column_defs))
                        schema_sql.append(");")
                        schema_sql.append("")
            
            # Записываем в файл
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(schema_sql))
            
            print(f"✅ Дамп схемы сохранён в {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Ошибка создания дампа схемы: {e}")
            return None


def main():
    """CLI интерфейс для менеджера миграций"""
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python migration_manager.py migrate    - выполнить все миграции")
        print("  python migration_manager.py status     - показать статус")
        print("  python migration_manager.py dump       - создать дамп схемы")
        sys.exit(1)
    
    # Получаем DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Переменная DATABASE_URL не установлена")
        sys.exit(1)
    
    manager = MigrationManager(database_url)
    command = sys.argv[1]
    
    if command == "migrate":
        success = manager.migrate()
        sys.exit(0 if success else 1)
    elif command == "status":
        manager.status()
    elif command == "dump":
        manager.create_schema_dump()
    else:
        print(f"❌ Неизвестная команда: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()