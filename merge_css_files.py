#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт объединения CSS файлов в единый ui-components.css
Объединяет все стили в один файл для оптимизации загрузки
"""

import os
import re
from datetime import datetime
from typing import Dict, List

# Конфигурация
DASHBOARD_DIR = "/Users/d.dubenetskiy/Documents/tg_project/dashboard"

# Файлы для объединения (в порядке приоритета)
CSS_FILES_TO_MERGE = [
    'dashboard-styles.css',      # Основные стили (переменные, базовые компоненты)
    'navigation-api-simple.css', # Стили навигации
    'unified-page-styles.css'    # Унифицированные стили страниц
]

# HTML страницы для обновления
HTML_PAGES = [
    'main.html', 'tasks.html', 'meetings.html', 'projects.html',
    'shopping.html', 'notes.html', 'settings.html', 'ui-kit.html'
]

def read_css_file(file_path: str) -> str:
    """Читает CSS файл и возвращает содержимое"""
    
    if not os.path.exists(file_path):
        print(f"⚠️ Файл не найден: {file_path}")
        return ""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"❌ Ошибка чтения {file_path}: {e}")
        return ""

def remove_duplicate_classes(content: str, existing_classes: set) -> tuple:
    """Удаляет дублирующиеся CSS классы"""
    
    lines = content.split('\n')
    filtered_lines = []
    current_class = None
    skip_block = False
    new_classes = set()
    
    for line in lines:
        # Ищем начало CSS класса
        class_match = re.match(r'^\s*\.([a-zA-Z][a-zA-Z0-9_-]*)\s*\{', line)
        
        if class_match:
            current_class = class_match.group(1)
            
            # Проверяем, есть ли уже такой класс
            if current_class in existing_classes:
                skip_block = True
                print(f"   🔄 Пропущен дублирующийся класс: .{current_class}")
                continue
            else:
                new_classes.add(current_class)
                skip_block = False
        
        # Ищем конец блока
        if skip_block and line.strip() == '}':
            skip_block = False
            continue
        
        # Добавляем строку если не пропускаем блок
        if not skip_block:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines), new_classes

def clean_css_content(content: str, file_name: str) -> str:
    """Очищает и форматирует CSS контент"""
    
    # Убираем лишние пустые строки
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Убираем blur эффекты если они остались
    content = re.sub(r'backdrop-filter:[^;]+;', '/* backdrop-filter removed */', content)
    content = re.sub(r'-webkit-backdrop-filter:[^;]+;', '/* -webkit-backdrop-filter removed */', content)
    
    # Добавляем заголовок секции
    section_headers = {
        'dashboard-styles.css': '/* ===== DASHBOARD BASE STYLES ===== */',
        'navigation-api-simple.css': '/* ===== NAVIGATION STYLES ===== */',
        'unified-page-styles.css': '/* ===== UNIFIED PAGE STYLES ===== */'
    }
    
    header = section_headers.get(file_name, f'/* ===== {file_name.upper()} ===== */')
    
    return f"\n\n{header}\n\n{content}"

def merge_css_files() -> str:
    """Объединяет все CSS файлы в один"""
    
    print("🔄 Объединение CSS файлов...")
    
    # Читаем базовый ui-components.css
    ui_kit_path = os.path.join(DASHBOARD_DIR, 'ui-components.css')
    merged_content = read_css_file(ui_kit_path)
    
    if not merged_content:
        print("❌ Не удалось прочитать ui-components.css")
        return ""
    
    print(f"✅ Базовый файл ui-components.css загружен ({len(merged_content)} символов)")
    
    # Извлекаем существующие классы из ui-components.css
    existing_classes = set(re.findall(r'\.([a-zA-Z][a-zA-Z0-9_-]*)\s*\{', merged_content))
    print(f"📊 Найдено классов в ui-components.css: {len(existing_classes)}")
    
    # Объединяем остальные файлы
    total_added = 0
    
    for file_name in CSS_FILES_TO_MERGE:
        file_path = os.path.join(DASHBOARD_DIR, file_name)
        content = read_css_file(file_path)
        
        if content:
            print(f"\n🔄 Обрабатываем {file_name}...")
            
            # Удаляем дублирующиеся классы
            cleaned_content, new_classes = remove_duplicate_classes(content, existing_classes)
            
            if new_classes:
                # Форматируем контент
                formatted_content = clean_css_content(cleaned_content, file_name)
                
                # Добавляем к общему контенту
                merged_content += formatted_content
                existing_classes.update(new_classes)
                total_added += len(new_classes)
                
                print(f"   ✅ Добавлено классов: {len(new_classes)}")
            else:
                print(f"   ⚠️ Все классы уже существуют, файл пропущен")
    
    print(f"\n📊 Итого добавлено новых классов: {total_added}")
    print(f"📏 Размер объединенного файла: {len(merged_content)} символов")
    
    return merged_content

def update_html_pages():
    """Обновляет HTML страницы - убирает лишние CSS подключения"""
    
    print("\n🔄 Обновление HTML страниц...")
    
    updated_count = 0
    
    for page_name in HTML_PAGES:
        page_path = os.path.join(DASHBOARD_DIR, page_name)
        
        if not os.path.exists(page_path):
            print(f"⚠️ Страница не найдена: {page_name}")
            continue
        
        try:
            # Читаем файл
            with open(page_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Создаем бэкап
            backup_path = page_path + '.backup-css-merge'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Убираем лишние CSS подключения
            original_content = content
            
            # Убираем подключения файлов которые мы объединили
            content = re.sub(r'<link rel="stylesheet" href="dashboard-styles\.css">\s*', '', content)
            content = re.sub(r'<link rel="stylesheet" href="navigation-api-simple\.css">\s*', '', content)
            content = re.sub(r'<link rel="stylesheet" href="unified-page-styles\.css">\s*', '', content)
            
            # Убираем лишние переносы строк
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            # Сохраняем обновленный файл
            if content != original_content:
                with open(page_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   ✅ Обновлен: {page_name}")
                updated_count += 1
            else:
                print(f"   ⚪ Без изменений: {page_name}")
                
        except Exception as e:
            print(f"   ❌ Ошибка обновления {page_name}: {e}")
    
    print(f"\n📊 Обновлено HTML страниц: {updated_count}/{len(HTML_PAGES)}")

def create_backup_and_save(merged_content: str):
    """Создает бэкап и сохраняет новый ui-components.css"""
    
    ui_kit_path = os.path.join(DASHBOARD_DIR, 'ui-components.css')
    
    # Создаем бэкап оригинального ui-components.css
    backup_path = ui_kit_path + '.backup-before-merge'
    
    try:
        with open(ui_kit_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        print(f"💾 Создан бэкап: ui-components.css.backup-before-merge")
        
        # Добавляем заголовок к объединенному файлу
        header = f"""/* ===== UNIFIED UI COMPONENTS CSS ===== */
/*
 * Объединенный CSS файл для Dashboard
 * Создан: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * 
 * Включает стили из:
 * - ui-components.css (базовый UI кит)
 * - dashboard-styles.css (основные стили)
 * - navigation-api-simple.css (навигация)
 * - unified-page-styles.css (унифицированные страницы)
 */

"""
        
        final_content = header + merged_content
        
        # Сохраняем новый файл
        with open(ui_kit_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"✅ Сохранен обновленный ui-components.css ({len(final_content)} символов)")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False

def main():
    """Основная функция"""
    
    print("🎨 Объединение CSS файлов в единый UI кит")
    print("=" * 50)
    
    # Объединяем CSS файлы
    merged_content = merge_css_files()
    
    if not merged_content:
        print("❌ Не удалось объединить CSS файлы")
        return
    
    # Создаем бэкап и сохраняем
    if not create_backup_and_save(merged_content):
        print("❌ Не удалось сохранить объединенный файл")
        return
    
    # Обновляем HTML страницы
    update_html_pages()
    
    print(f"\n🎉 Рефакторинг CSS завершен!")
    print(f"✅ Результат:")
    print(f"   📁 Было: 4 CSS файла")
    print(f"   📁 Стало: 1 CSS файл (ui-components.css)")
    print(f"   📊 HTML страниц обновлено")
    print(f"   💾 Созданы бэкапы всех файлов")
    
    print(f"\n🧪 Для проверки:")
    print(f"   🌐 Откройте любую страницу dashboard")
    print(f"   🔍 Проверьте, что стили применяются корректно")
    print(f"   📱 Протестируйте мобильную версию")
    
    print(f"\n📁 Файлы для удаления (после проверки):")
    for file_name in CSS_FILES_TO_MERGE:
        print(f"   🗑️ {file_name}")

if __name__ == "__main__":
    main()