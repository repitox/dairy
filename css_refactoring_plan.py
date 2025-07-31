#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
План рефакторинга CSS файлов Dashboard
Цель: объединить все стили в ui-components.css как основной UI кит
"""

import os
import re
from typing import Dict, List, Set

# Конфигурация
DASHBOARD_DIR = "/Users/d.dubenetskiy/Documents/tg_project/dashboard"

# Текущие CSS файлы для анализа
CSS_FILES = {
    'ui-components.css': 'UI кит - основной файл',
    'dashboard-styles.css': 'Основные стили dashboard',
    'navigation-api-simple.css': 'Стили навигации',
    'unified-page-styles.css': 'Унифицированные стили страниц'
}

# HTML страницы для обновления
HTML_PAGES = [
    'main.html', 'tasks.html', 'meetings.html', 'projects.html',
    'shopping.html', 'notes.html', 'settings.html'
]

def analyze_css_file(file_path: str) -> Dict:
    """Анализирует CSS файл и извлекает классы"""
    
    if not os.path.exists(file_path):
        return {'classes': set(), 'variables': set(), 'content': ''}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Извлекаем CSS классы
        class_pattern = r'\.([a-zA-Z][a-zA-Z0-9_-]*)\s*\{'
        classes = set(re.findall(class_pattern, content))
        
        # Извлекаем CSS переменные
        var_pattern = r'--([a-zA-Z][a-zA-Z0-9_-]*)'
        variables = set(re.findall(var_pattern, content))
        
        return {
            'classes': classes,
            'variables': variables,
            'content': content,
            'size': len(content)
        }
        
    except Exception as e:
        print(f"❌ Ошибка анализа {file_path}: {e}")
        return {'classes': set(), 'variables': set(), 'content': ''}

def find_duplicate_classes(css_files_data: Dict) -> Dict:
    """Находит дублирующиеся классы между файлами"""
    
    all_classes = {}
    duplicates = {}
    
    for file_name, data in css_files_data.items():
        for class_name in data['classes']:
            if class_name not in all_classes:
                all_classes[class_name] = []
            all_classes[class_name].append(file_name)
    
    # Находим дубликаты
    for class_name, files in all_classes.items():
        if len(files) > 1:
            duplicates[class_name] = files
    
    return duplicates

def categorize_styles() -> Dict:
    """Категоризирует стили по назначению"""
    
    return {
        'navigation': {
            'description': 'Стили навигации (navbar, sidebar, dropdown)',
            'classes': [
                'api-navbar', 'api-sidebar', 'api-nav-item', 'api-user-dropdown',
                'api-navbar-user', 'api-navbar-brand', 'api-menu-item'
            ],
            'source_file': 'navigation-api-simple.css'
        },
        'page_layout': {
            'description': 'Стили макета страниц (контейнеры, заголовки)',
            'classes': [
                'unified-page-container', 'unified-page-header', 'unified-page-title',
                'unified-action-btn', 'unified-secondary-btn'
            ],
            'source_file': 'unified-page-styles.css'
        },
        'components': {
            'description': 'UI компоненты (кнопки, карточки, формы)',
            'classes': [
                'btn', 'btn-primary', 'btn-secondary', 'card', 'glass-container',
                'form-group', 'form-input', 'modal'
            ],
            'source_file': 'dashboard-styles.css + ui-components.css'
        },
        'specific': {
            'description': 'Специфичные стили для конкретных страниц',
            'classes': [
                'dashboard-grid', 'tasks-container', 'meetings-header',
                'shopping-header', 'notes-content'
            ],
            'source_file': 'inline styles в HTML'
        }
    }

def create_refactoring_plan() -> Dict:
    """Создает план рефакторинга"""
    
    return {
        'step1': {
            'title': 'Анализ текущих файлов',
            'actions': [
                'Проанализировать все CSS файлы',
                'Найти дублирующиеся классы',
                'Определить зависимости между стилями'
            ]
        },
        'step2': {
            'title': 'Объединение в ui-components.css',
            'actions': [
                'Перенести стили кнопок из dashboard-styles.css',
                'Добавить стили навигации из navigation-api-simple.css',
                'Интегрировать unified-page-styles.css',
                'Убрать дублирующиеся стили'
            ]
        },
        'step3': {
            'title': 'Оптимизация структуры',
            'actions': [
                'Организовать стили по категориям',
                'Добавить комментарии и разделители',
                'Оптимизировать CSS переменные',
                'Убрать неиспользуемые стили'
            ]
        },
        'step4': {
            'title': 'Обновление HTML страниц',
            'actions': [
                'Заменить подключение 4 CSS файлов на 1',
                'Обновить классы в HTML при необходимости',
                'Протестировать все страницы',
                'Создать бэкапы'
            ]
        }
    }

def main():
    """Основная функция анализа"""
    
    print("🔍 Анализ CSS файлов для рефакторинга")
    print("=" * 50)
    
    # Анализируем все CSS файлы
    css_data = {}
    total_size = 0
    
    for file_name, description in CSS_FILES.items():
        file_path = os.path.join(DASHBOARD_DIR, file_name)
        data = analyze_css_file(file_path)
        css_data[file_name] = data
        total_size += data['size']
        
        print(f"\n📁 {file_name}")
        print(f"   📝 {description}")
        print(f"   📊 Классов: {len(data['classes'])}")
        print(f"   🎨 Переменных: {len(data['variables'])}")
        print(f"   📏 Размер: {data['size']} символов")
        
        if len(data['classes']) > 0:
            print(f"   🏷️  Примеры классов: {', '.join(list(data['classes'])[:5])}")
    
    print(f"\n📊 Общая статистика:")
    print(f"   📁 Файлов: {len(CSS_FILES)}")
    print(f"   📏 Общий размер: {total_size} символов")
    
    # Находим дубликаты
    duplicates = find_duplicate_classes(css_data)
    if duplicates:
        print(f"\n⚠️  Найдены дублирующиеся классы:")
        for class_name, files in duplicates.items():
            print(f"   🔄 .{class_name} в файлах: {', '.join(files)}")
    else:
        print(f"\n✅ Дублирующихся классов не найдено")
    
    # Показываем план рефакторинга
    plan = create_refactoring_plan()
    print(f"\n🎯 План рефакторинга:")
    
    for step_key, step_data in plan.items():
        print(f"\n{step_key.upper()}: {step_data['title']}")
        for action in step_data['actions']:
            print(f"   • {action}")
    
    # Показываем категории стилей
    categories = categorize_styles()
    print(f"\n📂 Категории стилей для объединения:")
    
    for cat_key, cat_data in categories.items():
        print(f"\n🏷️  {cat_key.upper()}: {cat_data['description']}")
        print(f"   📁 Источник: {cat_data['source_file']}")
        print(f"   🎨 Примеры: {', '.join(cat_data['classes'][:3])}")
    
    print(f"\n🎯 Цель рефакторинга:")
    print(f"   ❌ Было: 4 CSS файла ({total_size} символов)")
    print(f"   ✅ Будет: 1 CSS файл (ui-components.css)")
    print(f"   📈 Преимущества:")
    print(f"      • Меньше HTTP запросов")
    print(f"      • Централизованное управление стилями")
    print(f"      • Легче поддержка и обновления")
    print(f"      • Консистентность UI компонентов")

if __name__ == "__main__":
    main()