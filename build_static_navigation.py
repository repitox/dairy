#!/usr/bin/env python3
"""
Build-time инжектор статической навигации
Автоматически вставляет навигацию в HTML файлы без JavaScript загрузки
"""

import os
import re
from pathlib import Path

def inject_static_navigation(html_file_path, navigation_html):
    """Инжектирует статическую навигацию в HTML файл"""
    
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, не добавлена ли уже статическая навигация
    if 'static-navbar' in content:
        print(f"✅ {html_file_path.name} уже содержит статическую навигацию")
        return False
    
    # Удаляем старые скрипты навигации
    patterns_to_remove = [
        r'<script src="navigation-loader\.js"></script>',
        r'<script src="main-navigation\.js"></script>',
        r'<link rel="stylesheet" href="navigation-skeleton\.css">',
        r'<link rel="preload" href="navigation-component\.html"[^>]*>',
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # Добавляем CSS для статической навигации после navigation.css
    nav_css_pattern = r'(<link[^>]*href="navigation\.css"[^>]*>)'
    nav_css_match = re.search(nav_css_pattern, content, re.IGNORECASE)
    
    if nav_css_match:
        static_css = '\n    <link rel="stylesheet" href="navigation-static.css">'
        content = content.replace(nav_css_match.group(1), nav_css_match.group(1) + static_css)
    
    # Вставляем навигацию сразу после открытия <body>
    body_pattern = r'(<body[^>]*>)'
    body_match = re.search(body_pattern, content, re.IGNORECASE | re.DOTALL)
    
    if body_match:
        content = content.replace(body_match.group(1), body_match.group(1) + '\n' + navigation_html + '\n')
    else:
        print(f"❌ Не найден тег <body> в {html_file_path.name}")
        return False
    
    # Оборачиваем основной контент в static-main-content
    # Ищем div с классом container или основной контент
    container_pattern = r'(<div class="container"[^>]*>)'
    if re.search(container_pattern, content, re.IGNORECASE):
        content = re.sub(
            container_pattern, 
            r'<div class="static-main-content">\1', 
            content, 
            flags=re.IGNORECASE
        )
        # Закрываем static-main-content перед закрытием body
        content = content.replace('</body>', '</div>\n</body>')
    
    # Записываем обновленный файл
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    """Основная функция для инжекции статической навигации"""
    
    dashboard_dir = Path('/Users/d.dubenetskiy/Documents/tg_project/dashboard')
    navigation_file = dashboard_dir / 'navigation-static.html'
    
    if not navigation_file.exists():
        print("❌ Файл navigation-static.html не найден")
        return
    
    # Читаем шаблон навигации
    with open(navigation_file, 'r', encoding='utf-8') as f:
        navigation_html = f.read()
    
    # Находим HTML файлы (исключаем служебные)
    html_files = []
    exclude_files = {
        'navigation-component.html', 
        'navigation-static.html',
        'navbar-component.html',
        'navbar-demo.html',
        'test-navigation.html'
    }
    
    for html_file in dashboard_dir.glob('*.html'):
        if html_file.name not in exclude_files:
            # Проверяем, что файл содержит основной контент (есть container)
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'class="container"' in content:
                        html_files.append(html_file)
            except Exception as e:
                print(f"⚠️ Ошибка чтения {html_file.name}: {e}")
    
    print(f"🔍 Найдено {len(html_files)} HTML файлов для обновления:")
    for file in html_files:
        print(f"  - {file.name}")
    
    print("\n🔧 Начинаем инжекцию статической навигации...")
    
    updated_count = 0
    for html_file in html_files:
        try:
            if inject_static_navigation(html_file, navigation_html):
                print(f"✅ Обновлен {html_file.name}")
                updated_count += 1
            else:
                print(f"⚪ Пропущен {html_file.name}")
        except Exception as e:
            print(f"❌ Ошибка обновления {html_file.name}: {e}")
    
    print(f"\n🎉 Завершено! Обновлено {updated_count} из {len(html_files)} файлов")
    print("\n📋 Что было сделано:")
    print("  ✅ Удалены старые скрипты navigation-loader.js")
    print("  ✅ Добавлена статическая навигация в <body>")
    print("  ✅ Подключен navigation-static.css")
    print("  ✅ Контент обернут в static-main-content")
    print("\n🚀 Теперь навигация загружается мгновенно - без прыжков!")

if __name__ == "__main__":
    main()