#!/usr/bin/env python3
"""
Скрипт для поиска правильного пути к проекту на сервере
"""

import subprocess
import sys

def run_ssh_command(command, timeout=30):
    """Выполнить команду на удаленном сервере через SSH"""
    try:
        ssh_command = [
            'sshpass', '-p', 'YiKceHokjelen89',
            'ssh', '-o', 'StrictHostKeyChecking=no',
            'c107597@h60.netangels.ru',
            command
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
        
    except Exception as e:
        print(f"❌ Ошибка SSH: {e}")
        return None

def main():
    print("🔍 Поиск проекта на сервере")
    print("=" * 40)
    
    # Проверяем домашнюю директорию
    print("📁 Содержимое домашней директории:")
    home_content = run_ssh_command("ls -la")
    if home_content:
        print(home_content)
        print()
    
    # Ищем директории с доменами
    print("🌐 Поиск директорий с доменами:")
    domains_search = run_ssh_command("find . -name '*dialist*' -type d 2>/dev/null")
    if domains_search:
        print("Найденные директории с dialist:")
        print(domains_search)
        print()
    
    # Проверяем стандартные пути
    paths_to_check = [
        "domains",
        "www",
        "public_html",
        "dialist.ru",
        "htdocs"
    ]
    
    for path in paths_to_check:
        print(f"📂 Проверяем путь: {path}")
        result = run_ssh_command(f"ls -la {path} 2>/dev/null || echo 'Путь не найден'")
        if result and "Путь не найден" not in result:
            print(f"✅ Найден путь: {path}")
            print(result[:300] + "..." if len(result) > 300 else result)
            print()
    
    # Поиск Python файлов
    print("🐍 Поиск Python файлов проекта:")
    python_search = run_ssh_command("find . -name 'bot.py' -o -name 'run.py' 2>/dev/null")
    if python_search:
        print("Найденные Python файлы:")
        print(python_search)
        print()
    
    # Поиск по содержимому
    print("📝 Поиск файлов с 'dialist' в содержимом:")
    content_search = run_ssh_command("grep -r 'dialist' . --include='*.py' --include='*.html' 2>/dev/null | head -5")
    if content_search:
        print("Файлы с упоминанием dialist:")
        print(content_search)

if __name__ == "__main__":
    main()