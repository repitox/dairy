#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для унификации стилей страниц dashboard
Приводит все страницы к единому стилю заголовков и контейнеров
"""

import os
import re
from typing import Dict, List, Tuple

# Конфигурация
DASHBOARD_DIR = "/Users/d.dubenetskiy/Documents/tg_project/dashboard"

# Основные страницы для обновления
MAIN_PAGES = {
    'main.html': {
        'title': 'Главная',
        'icon': '🏠',
        'action_btn': None  # На главной нет кнопки добавления
    },
    'tasks.html': {
        'title': 'Задачи',
        'icon': '📋',
        'action_btn': {
            'text': 'Добавить задачу',
            'onclick': 'addTask()',
            'icon': '+'
        }
    },
    'meetings.html': {
        'title': 'Встречи',
        'icon': '📅',
        'action_btn': {
            'text': 'Добавить встречу',
            'onclick': 'addMeeting()',
            'icon': '+'
        }
    },
    'projects.html': {
        'title': 'Проекты',
        'icon': '📁',
        'action_btn': {
            'text': 'Создать проект',
            'onclick': 'createProject()',
            'icon': '+'
        }
    },
    'shopping.html': {
        'title': 'Покупки',
        'icon': '🛒',
        'action_btn': {
            'text': 'Добавить список',
            'onclick': 'addShoppingList()',
            'icon': '+'
        }
    },
    'notes.html': {
        'title': 'Заметки',
        'icon': '📝',
        'action_btn': {
            'text': 'Создать заметку',
            'onclick': 'createNote()',
            'icon': '+'
        }
    },
    'settings.html': {
        'title': 'Настройки',
        'icon': '⚙️',
        'action_btn': None  # На настройках нет кнопки добавления
    }
}

def add_unified_css_link(content: str) -> str:
    """Добавляет ссылку на unified-page-styles.css если её нет"""
    
    # Проверяем, есть ли уже ссылка
    if 'unified-page-styles.css' in content:
        return content
    
    # Ищем место для вставки (после navigation-api-simple.css)
    pattern = r'(<link rel="stylesheet" href="navigation-api-simple\.css">)'
    replacement = r'\1\n    <link rel="stylesheet" href="unified-page-styles.css">'
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
    else:
        # Если не найден navigation-api-simple.css, добавляем в head
        head_pattern = r'(</head>)'
        css_link = '    <link rel="stylesheet" href="unified-page-styles.css">\n'
        content = re.sub(head_pattern, css_link + r'\1', content)
    
    return content

def generate_unified_header(page_config: Dict) -> str:
    """Генерирует унифицированный заголовок страницы"""
    
    title = page_config['title']
    icon = page_config['icon']
    action_btn = page_config.get('action_btn')
    
    header_html = f'''        <div class="unified-page-header">
            <h1 class="unified-page-title">
                <span class="unified-page-title-icon">{icon}</span>
                <span class="unified-page-title-text">{title}</span>
            </h1>'''
    
    if action_btn:
        header_html += f'''
            <div class="unified-action-group">
                <button class="unified-action-btn" onclick="{action_btn['onclick']}">
                    <span class="unified-action-btn-icon">{action_btn['icon']}</span>
                    {action_btn['text']}
                </button>
            </div>'''
    
    header_html += '\n        </div>'
    
    return header_html

def update_page_structure(content: str, filename: str) -> str:
    """Обновляет структуру страницы под унифицированный стиль"""
    
    page_config = MAIN_PAGES[filename]
    
    # Генерируем новый заголовок
    new_header = generate_unified_header(page_config)
    
    # Паттерны для поиска и замены контейнеров
    container_patterns = [
        # main.html - container
        (r'<div class="container"[^>]*>', '<div class="unified-page-container">'),
        
        # tasks.html - tasks-page-container
        (r'<div class="tasks-page-container"[^>]*>', '<div class="unified-page-container">'),
        
        # meetings.html - meetings-container
        (r'<div class="meetings-container"[^>]*>', '<div class="unified-page-container">'),
        
        # projects.html - main-content + container
        (r'<main class="main-content">\s*<div class="container"[^>]*>', '<div class="unified-page-container">'),
        
        # shopping.html - shopping-container
        (r'<div class="shopping-container"[^>]*>', '<div class="unified-page-container">'),
        
        # notes.html - notes-container
        (r'<div class="notes-container"[^>]*>', '<div class="unified-page-container">'),
        
        # settings.html - settings-container
        (r'<div class="settings-container"[^>]*>', '<div class="unified-page-container">'),
    ]
    
    # Применяем замены контейнеров
    for pattern, replacement in container_patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Паттерны для поиска и замены заголовков
    header_patterns = [
        # Заголовок с кнопкой (meetings, shopping, tasks)
        (r'<div class="[^"]*header[^"]*"[^>]*>.*?</div>', new_header, re.MULTILINE | re.DOTALL),
        
        # Простой заголовок H1
        (r'<h1[^>]*>.*?</h1>', new_header, re.MULTILINE | re.DOTALL),
        
        # Заголовок в projects.html
        (r'<div class="page-header"[^>]*>.*?</div>', new_header, re.MULTILINE | re.DOTALL),
    ]
    
    # Применяем замены заголовков
    for pattern, replacement, flags in header_patterns:
        if re.search(pattern, content, flags):
            content = re.sub(pattern, replacement, content, flags)
            break  # Заменяем только первое вхождение
    
    # Закрываем контейнеры правильно
    closing_patterns = [
        # Закрытие main + container в projects.html
        (r'</div>\s*</main>', '</div>'),
        
        # Убираем лишние закрывающие теги если есть
        (r'</div>\s*</div>\s*$', '</div>', re.MULTILINE),
    ]
    
    for pattern, replacement, *flags in closing_patterns:
        flag = flags[0] if flags else 0
        content = re.sub(pattern, replacement, content, flag)
    
    return content

def backup_file(file_path: str) -> str:
    """Создает резервную копию файла"""
    backup_path = file_path + '.backup-unify'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return backup_path
    except Exception as e:
        print(f"❌ Ошибка создания бэкапа {file_path}: {e}")
        return None

def update_page(filename: str) -> bool:
    """Обновляет одну страницу"""
    
    file_path = os.path.join(DASHBOARD_DIR, filename)
    
    if not os.path.exists(file_path):
        print(f"⚠️ Файл не найден: {filename}")
        return False
    
    try:
        # Создаем бэкап
        backup_path = backup_file(file_path)
        if backup_path:
            print(f"💾 Создан бэкап: {os.path.basename(backup_path)}")
        
        # Читаем файл
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Добавляем CSS ссылку
        content = add_unified_css_link(content)
        
        # Обновляем структуру
        content = update_page_structure(content, filename)
        
        # Сохраняем файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Обновлен: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления {filename}: {e}")
        return False

def main():
    """Основная функция"""
    print("🎨 Унификация стилей страниц dashboard")
    print("=" * 50)
    
    # Проверяем, что CSS файл существует
    css_path = os.path.join(DASHBOARD_DIR, 'unified-page-styles.css')
    if not os.path.exists(css_path):
        print(f"❌ CSS файл не найден: {css_path}")
        print("Создайте файл unified-page-styles.css перед запуском скрипта")
        return
    
    print(f"✅ CSS файл найден: unified-page-styles.css")
    
    # Обновляем все страницы
    updated_count = 0
    total_count = len(MAIN_PAGES)
    
    for filename in MAIN_PAGES.keys():
        print(f"\n🔄 Обрабатываем: {filename}")
        
        if update_page(filename):
            updated_count += 1
        else:
            print(f"⚠️ Пропущен: {filename}")
    
    print(f"\n🎉 Унификация завершена!")
    print(f"✅ Обновлено страниц: {updated_count}/{total_count}")
    
    if updated_count > 0:
        print(f"\n📝 Изменения:")
        print(f"  • Добавлен unified-page-styles.css во все страницы")
        print(f"  • Контейнеры прижаты влево (убрано центрирование)")
        print(f"  • Унифицированы заголовки H1 с иконками")
        print(f"  • Добавлены кнопки действий где необходимо")
        print(f"  • Созданы бэкапы всех файлов (.backup-unify)")
        
        print(f"\n🧪 Для проверки откройте:")
        for filename in MAIN_PAGES.keys():
            page_name = MAIN_PAGES[filename]['title']
            print(f"  🌐 http://localhost:8000/dashboard/{filename} - {page_name}")

if __name__ == "__main__":
    main()