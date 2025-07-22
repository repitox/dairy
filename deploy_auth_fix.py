#!/usr/bin/env python3
"""
Быстрый деплой исправлений авторизации на продакшн
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Выполнить команду с описанием"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - успешно")
        if result.stdout:
            print(f"📝 Вывод: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ошибка")
        print(f"💥 Код ошибки: {e.returncode}")
        if e.stdout:
            print(f"📝 Stdout: {e.stdout}")
        if e.stderr:
            print(f"📝 Stderr: {e.stderr}")
        return False

def main():
    """Основная функция деплоя"""
    print("🚀 Деплой исправлений авторизации на продакшн")
    print("=" * 50)
    
    # Список файлов для загрузки
    files_to_upload = [
        "db.py",
        "bot.py"
    ]
    
    # Загружаем файлы на сервер
    for file in files_to_upload:
        if not os.path.exists(file):
            print(f"❌ Файл {file} не найден")
            return False
        
        command = f"scp {file} c107597@h60.netangels.ru:~/rptx.na4u.ru/"
        if not run_command(command, f"Загрузка {file}"):
            return False
    
    # Перезапускаем приложение
    restart_command = "ssh c107597@h60.netangels.ru 'cd ~/rptx.na4u.ru && touch reload'"
    if not run_command(restart_command, "Перезапуск приложения"):
        return False
    
    print("\n🎉 Деплой завершен успешно!")
    print("⏰ Подождите 10-15 секунд для применения изменений")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)