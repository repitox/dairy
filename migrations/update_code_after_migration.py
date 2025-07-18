#!/usr/bin/env python3
"""
Скрипт для обновления кода приложения после миграции реструктуризации пользователей
Этот скрипт обновляет все функции в db.py для работы с новой структурой
"""

import sys
import os
import re

def update_db_functions():
    """Обновление функций в db.py для работы с новой структурой"""
    print("🔄 Обновление функций в db.py...")
    
    db_file_path = "/Users/d.dubenetskiy/Documents/tg_project/db.py"
    
    try:
        with open(db_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Список замен для обновления кода
        replacements = [
            # Обновление функций аутентификации
            (r'SELECT \* FROM users WHERE user_id = %s', 'SELECT * FROM users WHERE telegram_id = %s'),
            (r'INSERT INTO users \(user_id,', 'INSERT INTO users (telegram_id,'),
            (r'ON CONFLICT \(user_id\)', 'ON CONFLICT (telegram_id)'),
            
            # Обновление JOIN-ов
            (r'JOIN users u ON u\.user_id = ', 'JOIN users u ON u.id = '),
            (r'FROM users u WHERE u\.user_id = ', 'FROM users u WHERE u.telegram_id = '),
            
            # Обновление функций создания записей
            (r'VALUES \(%s, %s, %s\).*-- user_id', 'VALUES (%s, %s, %s) -- user_id теперь ссылается на users.id'),
        ]
        
        updated_content = content
        changes_made = 0
        
        for old_pattern, new_pattern in replacements:
            if re.search(old_pattern, updated_content):
                updated_content = re.sub(old_pattern, new_pattern, updated_content)
                changes_made += 1
                print(f"✅ Обновлен паттерн: {old_pattern[:50]}...")
        
        if changes_made > 0:
            # Создаем резервную копию
            with open(f"{db_file_path}.backup", 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Записываем обновленный код
            with open(db_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ Обновлено {changes_made} паттернов в db.py")
            print(f"💾 Резервная копия сохранена как db.py.backup")
        else:
            print("ℹ️  Автоматические обновления не требуются")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления db.py: {e}")
        return False

def create_new_auth_functions():
    """Создание новых функций аутентификации"""
    print("🔄 Создание новых функций аутентификации...")
    
    new_functions = '''
# === НОВЫЕ ФУНКЦИИ ПОСЛЕ МИГРАЦИИ ===

def get_user_by_telegram_id(telegram_id: int):
    """Получение пользователя по Telegram ID"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
            return cur.fetchone()

def get_user_by_id(user_id: int):
    """Получение пользователя по внутреннему ID"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cur.fetchone()

def create_user_new(telegram_id: int, first_name: str, username: str = None):
    """Создание нового пользователя (новая версия)"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (telegram_id, first_name, username, registered_at, theme)
                VALUES (%s, %s, %s, %s, 'light')
                ON CONFLICT (telegram_id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    username = EXCLUDED.username
                RETURNING id
            """, (telegram_id, first_name, username, datetime.utcnow().isoformat()))
            user_id = cur.fetchone()["id"]
            conn.commit()
            return user_id

# === КОНЕЦ НОВЫХ ФУНКЦИЙ ===
'''
    
    try:
        db_file_path = "/Users/d.dubenetskiy/Documents/tg_project/db.py"
        
        with open(db_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Добавляем новые функции в конец файла
        if "# === НОВЫЕ ФУНКЦИИ ПОСЛЕ МИГРАЦИИ ===" not in content:
            updated_content = content + new_functions
            
            with open(db_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("✅ Новые функции аутентификации добавлены")
        else:
            print("ℹ️  Новые функции уже существуют")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка добавления новых функций: {e}")
        return False

def create_migration_checklist():
    """Создание чек-листа для ручной проверки"""
    checklist = '''
# 📋 Чек-лист после миграции пользователей

## ✅ Автоматически обновлено:
- [ ] Функции в db.py обновлены
- [ ] Новые функции аутентификации добавлены
- [ ] Резервная копия db.py создана

## 🔍 Требует ручной проверки:

### 1. Функции аутентификации:
- [ ] `register_user()` - проверить использование telegram_id
- [ ] `get_user()` - обновить для работы с новой структурой
- [ ] Все места где используется user_id для поиска пользователя

### 2. API эндпоинты:
- [ ] `/api/auth` - проверить аутентификацию
- [ ] Все эндпоинты, которые работают с пользователями
- [ ] Проверить передачу user_id в запросах

### 3. Frontend код:
- [ ] JavaScript функции аутентификации
- [ ] Сохранение user_id в localStorage/sessionStorage
- [ ] AJAX запросы с user_id

### 4. Telegram Bot (если есть):
- [ ] Обновить функции работы с пользователями
- [ ] Проверить регистрацию новых пользователей

### 5. Тестирование:
- [ ] Регистрация нового пользователя
- [ ] Аутентификация существующего пользователя
- [ ] Создание задач/проектов/покупок
- [ ] Работа с участниками проектов
- [ ] Все основные функции приложения

## 🚨 Критические проверки:
- [ ] Все пользователи могут войти в систему
- [ ] Связи между таблицами работают корректно
- [ ] Нет потерянных данных
- [ ] Производительность не ухудшилась

## 📝 Заметки:
- Старые функции помечены как deprecated
- Новые функции используют users.id для связей
- telegram_id используется только для аутентификации
- Все внешние ключи теперь ссылаются на users.id
'''
    
    try:
        checklist_path = "/Users/d.dubenetskiy/Documents/tg_project/docs/POST_MIGRATION_CHECKLIST.md"
        
        with open(checklist_path, 'w', encoding='utf-8') as f:
            f.write(checklist)
        
        print(f"✅ Чек-лист создан: {checklist_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания чек-листа: {e}")
        return False

def main():
    """Главная функция обновления кода"""
    print("🚀 Обновление кода после миграции пользователей")
    print("=" * 60)
    
    success = True
    
    # Обновление функций в db.py
    if not update_db_functions():
        success = False
    
    # Создание новых функций
    if not create_new_auth_functions():
        success = False
    
    # Создание чек-листа
    if not create_migration_checklist():
        success = False
    
    if success:
        print("\n✅ Автоматическое обновление кода завершено!")
        print("📋 Проверьте файл docs/POST_MIGRATION_CHECKLIST.md")
        print("🔍 Выполните ручную проверку всех функций")
    else:
        print("\n❌ Обновление кода завершено с ошибками")
        print("🔍 Проверьте логи и выполните обновления вручную")

if __name__ == "__main__":
    main()