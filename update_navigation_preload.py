#!/usr/bin/env python3
"""
Скрипт для автоматического добавления preload и skeleton CSS 
во все HTML файлы dashboard для устранения "прыгания" навигации
"""

import os
import re
from pathlib import Path

def update_html_file(file_path):
    """Обновляет HTML файл, добавляя preload и skeleton CSS"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, есть ли уже preload и skeleton CSS
    if 'navigation-skeleton.css' in content and 'preload' in content:
        print(f"✅ {file_path.name} уже обновлен")
        return False
    
    # Ищем блок head и тег title
    title_pattern = r'(<title>.*?</title>)'
    title_match = re.search(title_pattern, content, re.IGNORECASE | re.DOTALL)
    
    if not title_match:
        print(f"❌ Не найден тег title в {file_path.name}")
        return False
    
    # Создаем блок preload и skeleton CSS
    preload_block = '''
    <!-- Preload критических ресурсов для быстрой загрузки -->
    <link rel="preload" href="navigation-component.html" as="fetch" crossorigin>
    <link rel="preload" href="navigation.css" as="style">
    <link rel="preload" href="navigation-skeleton.css" as="style">'''
    
    # Ищем где подключается navigation.css
    nav_css_pattern = r'(<link[^>]*href="navigation\.css"[^>]*>)'
    nav_css_match = re.search(nav_css_pattern, content, re.IGNORECASE)
    
    if nav_css_match:
        # Добавляем skeleton CSS после navigation.css
        skeleton_css = '\n    <link rel="stylesheet" href="navigation-skeleton.css">'
        content = content.replace(nav_css_match.group(1), nav_css_match.group(1) + skeleton_css)
        
        # Добавляем preload блок после title
        content = content.replace(title_match.group(1), title_match.group(1) + preload_block)
        
    else:
        print(f"⚠️ Не найден navigation.css в {file_path.name}")
        return False
    
    # Записываем обновленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Обновлен {file_path.name}")
    return True

def main():
    """Основная функция для обновления всех HTML файлов"""
    
    dashboard_dir = Path('/Users/d.dubenetskiy/Documents/tg_project/dashboard')
    
    if not dashboard_dir.exists():
        print("❌ Папка dashboard не найдена")
        return
    
    # Находим все HTML файлы с navigation-loader.js
    html_files = []
    for html_file in dashboard_dir.glob('*.html'):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'navigation-loader.js' in content:
                    html_files.append(html_file)
        except Exception as e:
            print(f"⚠️ Ошибка чтения {html_file.name}: {e}")
    
    print(f"🔍 Найдено {len(html_files)} HTML файлов с навигацией:")
    for file in html_files:
        print(f"  - {file.name}")
    
    print("\n🔧 Начинаем обновление...")
    
    updated_count = 0
    for html_file in html_files:
        try:
            if update_html_file(html_file):
                updated_count += 1
        except Exception as e:
            print(f"❌ Ошибка обновления {html_file.name}: {e}")
    
    print(f"\n🎉 Завершено! Обновлено {updated_count} из {len(html_files)} файлов")
    print("\n📋 Что было добавлено:")
    print("  ✅ Preload для navigation-component.html")
    print("  ✅ Preload для navigation.css и navigation-skeleton.css")
    print("  ✅ Подключение navigation-skeleton.css")
    print("\n🚀 Теперь навигация будет загружаться без 'прыгания'!")

if __name__ == "__main__":
    main()