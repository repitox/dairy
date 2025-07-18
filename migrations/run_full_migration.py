#!/usr/bin/env python3
"""
ПОЛНАЯ МИГРАЦИЯ РЕСТРУКТУРИЗАЦИИ ПОЛЬЗОВАТЕЛЕЙ
⚠️  ВНИМАНИЕ: Этот скрипт изменяет структуру БД!
⚠️  Обязательно создайте резервную копию перед запуском!
"""

import sys
import os
import subprocess
from datetime import datetime

def print_banner():
    """Вывод баннера миграции"""
    print("=" * 80)
    print("🚀 ПОЛНАЯ МИГРАЦИЯ РЕСТРУКТУРИЗАЦИИ ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 80)
    print("📅 Дата:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🎯 Цель: Переход к классической структуре users с автоинкрементным id")
    print("⚠️  ВНИМАНИЕ: Это критическая миграция!")
    print("=" * 80)

def confirm_migration():
    """Подтверждение выполнения миграции"""
    print("\n🔍 Проверьте следующее перед продолжением:")
    print("✅ Создана резервная копия базы данных")
    print("✅ Приложение остановлено или переведено в режим обслуживания")
    print("✅ Все пользователи уведомлены о техническом обслуживании")
    print("✅ Есть план отката в случае проблем")
    
    print("\n📋 Что будет сделано:")
    print("1. Создание резервной копии всех данных")
    print("2. Добавление поля id в таблицу users")
    print("3. Создание временных колонок во всех связанных таблицах")
    print("4. Переключение на новые колонки")
    print("5. Финализация: установка внешних ключей")
    print("6. Обновление кода приложения")
    print("7. Проверка результатов")
    
    print("\n⏱️  Ожидаемое время выполнения: 5-15 минут")
    print("📊 Затронутые таблицы: users + 10 связанных таблиц")
    
    response = input("\n❓ Вы уверены, что хотите продолжить? Введите 'YES' для подтверждения: ")
    return response == 'YES'

def run_command(command, description):
    """Выполнение команды с логированием"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd="/Users/d.dubenetskiy/Documents/tg_project")
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            if result.stdout.strip():
                print(f"📝 Вывод: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - ошибка")
            print(f"📝 Ошибка: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - исключение: {e}")
        return False

def main():
    """Главная функция полной миграции"""
    print_banner()
    
    if not confirm_migration():
        print("❌ Миграция отменена пользователем")
        return
    
    print("\n🚀 Начинаем миграцию...")
    
    # Этап 1: Тестирование
    if not run_command("docker-compose exec app python migrations/test_migration.py", "Предварительное тестирование"):
        print("❌ Тестирование не пройдено. Миграция прервана.")
        return
    
    # Этап 2: Выполнение миграции БД
    if not run_command("docker-compose exec app python migrations/user_restructure_migration.py", "Выполнение миграции БД"):
        print("❌ Миграция БД не выполнена. Проверьте логи.")
        return
    
    # Этап 3: Обновление кода
    if not run_command("python migrations/update_code_after_migration.py", "Обновление кода приложения"):
        print("⚠️  Автоматическое обновление кода не выполнено. Требуется ручное обновление.")
    
    # Этап 4: Перезапуск приложения
    if not run_command("docker-compose restart app", "Перезапуск приложения"):
        print("⚠️  Не удалось перезапустить приложение. Сделайте это вручную.")
    
    print("\n" + "=" * 80)
    print("🎉 МИГРАЦИЯ ЗАВЕРШЕНА!")
    print("=" * 80)
    
    print("\n📋 Следующие шаги:")
    print("1. ✅ Проверьте работоспособность приложения")
    print("2. ✅ Выполните тестирование основных функций")
    print("3. ✅ Проверьте чек-лист: docs/POST_MIGRATION_CHECKLIST.md")
    print("4. ✅ Уведомите пользователей о завершении обслуживания")
    print("5. ✅ Мониторьте приложение в течение нескольких часов")
    
    print("\n🔍 Файлы для проверки:")
    print("- docs/POST_MIGRATION_CHECKLIST.md - чек-лист проверок")
    print("- db.py.backup - резервная копия кода")
    print("- Схема backup в БД - резервная копия данных")
    
    print("\n⚠️  В случае проблем:")
    print("- Используйте резервную копию для отката")
    print("- Проверьте логи приложения")
    print("- Обратитесь к документации миграции")
    
    print("\n🎯 Новая структура готова к использованию!")

if __name__ == "__main__":
    main()