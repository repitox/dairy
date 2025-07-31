#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для автоматического обновления страниц dashboard на новую API Navigation System
Дата: 31 января 2025
"""

import os
import re
import glob
from pathlib import Path

# Конфигурация
DASHBOARD_DIR = "/Users/d.dubenetskiy/Documents/tg_project/dashboard"
BACKUP_DIR = "/Users/d.dubenetskiy/Documents/tg_project/dashboard/backup_old_nav"

# Файлы для исключения из обновления
EXCLUDE_FILES = {
    'navbar-component.html',
    'navigation-component.html', 
    'main-api-test.html',  # Уже обновлен
    'main-static-test.html',
    'navigation-static.html',
    'navbar-demo.html',
    'ui-kit.html',  # UI Kit оставляем отдельно
    # Тестовые файлы
    'test-api.html',
    'test-user.html', 
    'test-user-sync.html',
    'test-meetings-api.html',
    'test-navigation.html',
    'debug-user-id.html'
}

def create_backup():
    """Создание резервной копии старых файлов"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"📁 Создана папка для бэкапов: {BACKUP_DIR}")

def get_html_files():
    """Получение списка HTML файлов для обновления"""
    pattern = os.path.join(DASHBOARD_DIR, "*.html")
    all_files = glob.glob(pattern)
    
    # Фильтруем файлы
    files_to_update = []
    for file_path in all_files:
        filename = os.path.basename(file_path)
        if filename not in EXCLUDE_FILES:
            files_to_update.append(file_path)
    
    return files_to_update

def backup_file(file_path):
    """Создание бэкапа файла"""
    filename = os.path.basename(file_path)
    backup_path = os.path.join(BACKUP_DIR, f"{filename}.backup")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"💾 Бэкап создан: {filename}")

def update_html_file(file_path):
    """Обновление HTML файла на новую API навигацию"""
    filename = os.path.basename(file_path)
    
    # Читаем файл
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Сохраняем оригинал
    backup_file(file_path)
    
    # Обновления в <head>
    # 1. Заменяем preload директивы
    old_preloads = [
        r'<link rel="preload" href="navigation-component\.html" as="fetch" crossorigin>',
        r'<link rel="preload" href="navigation\.css" as="style">',
        r'<link rel="preload" href="navigation-skeleton\.css" as="style">'
    ]
    
    new_preload = '    <link rel="preload" href="/api/navigation?category=main" as="fetch" crossorigin>'
    
    # Удаляем старые preload директивы
    for old_preload in old_preloads:
        content = re.sub(old_preload, '', content, flags=re.IGNORECASE)
    
    # Добавляем новый preload после последнего preload или после title
    if '<link rel="preload"' in content:
        content = re.sub(
            r'(\s*<link rel="preload"[^>]*>\s*)', 
            lambda m: m.group(1) + '\n' + new_preload + '\n    ',
            content, count=1
        )
    else:
        content = re.sub(
            r'(\s*<title>[^<]*</title>\s*)',
            lambda m: m.group(1) + '\n    ' + new_preload + '\n    ',
            content
        )
    
    # 2. Заменяем CSS файлы
    css_replacements = [
        (r'<link rel="stylesheet" href="navigation\.css">', ''),
        (r'<link rel="stylesheet" href="navigation-skeleton\.css">', ''),
    ]
    
    for old_css, new_css in css_replacements:
        content = re.sub(old_css, new_css, content, flags=re.IGNORECASE)
    
    # Добавляем новые CSS файлы после основных стилей
    dashboard_css_pattern = r'(\s*<link rel="stylesheet" href="dashboard-styles\.css">\s*)'
    replacement = r'\1    <link rel="stylesheet" href="navigation-api.css">\n'
    content = re.sub(dashboard_css_pattern, replacement, content)
    
    # 3. Обновляем скрипты в <body>
    # Заменяем старые скрипты навигации
    old_scripts = [
        r'<script src="navigation-loader\.js"></script>',
        r'<script src="main-navigation\.js"></script>',
    ]
    
    for old_script in old_scripts:
        content = re.sub(old_script, '', content, flags=re.IGNORECASE)
    
    # Добавляем новый скрипт API навигации
    # Ищем место после auth.js или в начале скриптов
    auth_script_pattern = r'(\s*<script src="auth\.js"></script>\s*)'
    new_script = '    <script src="navigation-api-loader.js"></script>\n'
    
    if re.search(auth_script_pattern, content):
        content = re.sub(auth_script_pattern, r'\1' + new_script, content)
    else:
        # Если нет auth.js, добавляем в начало body
        body_pattern = r'(\s*<body[^>]*>\s*)'
        content = re.sub(body_pattern, r'\1' + new_script, content)
    
    # 4. Удаляем комментарии про старую навигацию
    old_comments = [
        r'<!-- Навигация будет загружена автоматически -->\s*',
        r'<!-- Preload критических ресурсов для быстрой загрузки -->\s*',
    ]
    
    for comment in old_comments:
        content = re.sub(comment, '', content, flags=re.IGNORECASE)
    
    # 5. Добавляем комментарий про новую API навигацию
    body_pattern = r'(\s*<body[^>]*>\s*)'
    api_comment = '    <!-- API навигация загрузится автоматически через JavaScript -->\n    \n'
    content = re.sub(body_pattern, r'\1' + api_comment, content)
    
    # 6. Очищаем лишние пустые строки
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Убираем тройные переносы
    content = re.sub(r'^\s*\n', '', content, flags=re.MULTILINE)  # Убираем пустые строки в начале строк
    
    # Сохраняем обновленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Обновлен: {filename}")

def update_ui_kit_separately():
    """Отдельное обновление UI Kit с сохранением его особенностей"""
    ui_kit_path = os.path.join(DASHBOARD_DIR, "ui-kit.html")
    if not os.path.exists(ui_kit_path):
        return
    
    print("🎨 Обновляем UI Kit...")
    
    with open(ui_kit_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Создаем бэкап
    backup_file(ui_kit_path)
    
    # Минимальные изменения для UI Kit
    # Добавляем только новые CSS и JS файлы, но оставляем старые для совместимости
    
    # Добавляем новый CSS после основных стилей
    if 'navigation-api.css' not in content:
        dashboard_css_pattern = r'(\s*<link rel="stylesheet" href="ui-components\.css">\s*)'
        replacement = r'\1    <link rel="stylesheet" href="navigation-api.css">\n'
        content = re.sub(dashboard_css_pattern, replacement, content)
    
    # Добавляем новый JS в конец скриптов
    if 'navigation-api-loader.js' not in content:
        body_end_pattern = r'(\s*</body>)'
        new_script = '    <script src="navigation-api-loader.js"></script>\n'
        content = re.sub(body_end_pattern, new_script + r'\1', content)
    
    with open(ui_kit_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ UI Kit обновлен (гибридный режим)")

def main():
    """Основная функция"""
    print("🚀 Начинаем обновление страниц dashboard на API Navigation System")
    print("=" * 60)
    
    # Создаем бэкапы
    create_backup()
    
    # Получаем список файлов
    files_to_update = get_html_files()
    
    print(f"\n📋 Найдено {len(files_to_update)} файлов для обновления:")
    for file_path in files_to_update:
        print(f"  - {os.path.basename(file_path)}")
    
    print(f"\n🚫 Исключены из обновления:")
    for excluded in sorted(EXCLUDE_FILES):
        print(f"  - {excluded}")
    
    # Подтверждение
    print(f"\n⚠️  Все файлы будут обновлены!")
    print(f"💾 Бэкапы сохранены в: {BACKUP_DIR}")
    
    # Обновляем файлы
    print(f"\n🔄 Обновляем файлы...")
    updated_count = 0
    
    for file_path in files_to_update:
        try:
            update_html_file(file_path)
            updated_count += 1
        except Exception as e:
            print(f"❌ Ошибка обновления {os.path.basename(file_path)}: {e}")
    
    # Отдельно обновляем UI Kit
    try:
        update_ui_kit_separately()
    except Exception as e:
        print(f"❌ Ошибка обновления UI Kit: {e}")
    
    print(f"\n🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО!")
    print(f"✅ Успешно обновлено: {updated_count} файлов")
    print(f"🎨 UI Kit обновлен в гибридном режиме")
    print(f"💾 Бэкапы доступны в: {BACKUP_DIR}")
    
    print(f"\n📝 Что было изменено:")
    print(f"  ✅ Заменены preload директивы на API")
    print(f"  ✅ Подключены navigation-api.css")
    print(f"  ✅ Подключен navigation-api-loader.js")
    print(f"  ✅ Удалены старые navigation-*.js файлы")
    print(f"  ✅ Очищены лишние комментарии")
    
    print(f"\n🧪 Для тестирования откройте:")
    print(f"  🌐 http://localhost:8000/dashboard/main.html")
    print(f"  🌐 http://localhost:8000/dashboard/tasks.html")
    print(f"  🌐 http://localhost:8000/dashboard/meetings.html")

if __name__ == "__main__":
    main()