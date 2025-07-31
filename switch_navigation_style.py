#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для переключения стилей API навигации
Использование: python3 switch_navigation_style.py [simple|animated]
"""

import os
import sys
import glob
import re

# Конфигурация
DASHBOARD_DIR = "/Users/d.dubenetskiy/Documents/tg_project/dashboard"

def switch_to_style(style):
    """Переключить на указанный стиль"""
    if style not in ['simple', 'animated']:
        print("❌ Неверный стиль. Используйте: simple или animated")
        return False
    
    # Определяем целевой CSS файл
    target_css = "navigation-api-simple.css" if style == 'simple' else "navigation-api.css"
    old_css_1 = "navigation-api.css" if style == 'simple' else "navigation-api-simple.css"
    
    print(f"🔄 Переключаем на стиль: {style}")
    print(f"📁 Целевой CSS файл: {target_css}")
    
    # Проверяем, что целевой файл существует
    target_path = os.path.join(DASHBOARD_DIR, target_css)
    if not os.path.exists(target_path):
        print(f"❌ Файл {target_css} не найден!")
        return False
    
    # Получаем все HTML файлы
    pattern = os.path.join(DASHBOARD_DIR, "*.html")
    html_files = glob.glob(pattern)
    
    # Исключаем служебные файлы
    exclude_files = {
        'navbar-component.html', 'navigation-component.html',
        'test-api.html', 'test-user.html', 'debug-user-id.html'
    }
    
    files_to_update = []
    for file_path in html_files:
        filename = os.path.basename(file_path)
        if filename not in exclude_files:
            files_to_update.append(file_path)
    
    updated_count = 0
    
    for file_path in files_to_update:
        filename = os.path.basename(file_path)
        
        try:
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем, нужно ли обновлять
            if target_css in content:
                print(f"⏭️ Пропускаем {filename} (уже использует {target_css})")
                continue
            
            # Заменяем CSS файл
            original_content = content
            
            # Заменяем старый CSS файл на новый
            content = re.sub(
                r'<link rel="stylesheet" href="navigation-api(-simple)?\.css">',
                f'<link rel="stylesheet" href="{target_css}">',
                content
            )
            
            # Проверяем, произошли ли изменения
            if content != original_content:
                # Сохраняем файл
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Обновлен: {filename}")
                updated_count += 1
            else:
                print(f"⚠️ Не найден CSS в {filename}")
                
        except Exception as e:
            print(f"❌ Ошибка обновления {filename}: {e}")
    
    print(f"\n🎉 Переключение завершено!")
    print(f"✅ Обновлено файлов: {updated_count}")
    print(f"🎨 Активный стиль: {style}")
    print(f"📁 CSS файл: {target_css}")
    
    if style == 'simple':
        print(f"\n📝 Особенности простого стиля:")
        print(f"  • Без анимаций слева-направо")
        print(f"  • Без shimmer эффектов")
        print(f"  • Быстрое fade-in появление") 
        print(f"  • Статичная skeleton загрузка")
    else:
        print(f"\n📝 Особенности анимированного стиля:")
        print(f"  • Плавное fade-in появление")
        print(f"  • Мягкое мерцание skeleton")
        print(f"  • Более плавные переходы")
    
    print(f"\n🔄 Для применения изменений:")
    print(f"  1. Перезагрузите страницы dashboard")
    print(f"  2. Очистите кеш браузера (Ctrl+F5)")
    
    return True

def detect_current_style():
    """Определить текущий используемый стиль"""
    # Проверяем несколько основных файлов
    test_files = ['main.html', 'tasks.html', 'meetings.html']
    
    for filename in test_files:
        file_path = os.path.join(DASHBOARD_DIR, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'navigation-api-simple.css' in content:
                    return 'simple'
                elif 'navigation-api.css' in content:
                    return 'animated'
                    
            except Exception:
                continue
    
    return 'unknown'

def main():
    """Основная функция"""
    print("🎨 Navigation Style Switcher")
    print("=" * 40)
    
    # Определяем текущий стиль
    current_style = detect_current_style()
    if current_style != 'unknown':
        print(f"📊 Текущий стиль: {current_style}")
    else:
        print("⚠️ Не удалось определить текущий стиль")
    
    # Проверяем аргументы командной строки
    if len(sys.argv) < 2:
        print(f"\n💡 Использование:")
        print(f"  python3 {sys.argv[0]} simple     # Простой стиль без анимаций")
        print(f"  python3 {sys.argv[0]} animated   # Анимированный стиль")
        
        print(f"\n🎯 Доступные стили:")
        print(f"  📄 simple    - Без анимаций, быстрая загрузка")
        print(f"  ✨ animated  - С плавными анимациями")
        
        return
    
    target_style = sys.argv[1].lower()
    
    if current_style == target_style:
        print(f"\n✅ Стиль '{target_style}' уже активен!")
        return
    
    # Выполняем переключение
    success = switch_to_style(target_style)
    
    if success:
        print(f"\n🧪 Для тестирования откройте:")
        print(f"  🌐 http://localhost:8000/dashboard/main.html")
        print(f"  🔍 http://localhost:8000/dashboard/api-navigation-diagnostic.html")

if __name__ == "__main__":
    main()