#!/usr/bin/env python3
"""
Скрипт для массового исправления ссылок на user.id в HTML файлах dashboard
Заменяет user.id на Auth.getCurrentUserId() во всех HTML файлах
"""

import os
import re
import glob

def fix_user_id_references():
    dashboard_path = "/Users/d.dubenetskiy/Documents/tg_project/dashboard"
    html_files = glob.glob(os.path.join(dashboard_path, "*.html"))
    
    # Паттерны для замены
    patterns = [
        # API запросы с user.id в URL
        (r'user_id=\$\{user\.id\}', r'user_id=${Auth.getCurrentUserId()}'),
        
        # JSON body с user_id: user.id
        (r'user_id:\s*user\.id', r'user_id: Auth.getCurrentUserId()'),
        
        # Функции с параметром user.id
        (r'([a-zA-Z_][a-zA-Z0-9_]*)\(user\.id\)', r'\1(Auth.getCurrentUserId())'),
        
        # Присваивание user_id: user.id в объектах
        (r'"user_id":\s*user\.id', r'"user_id": Auth.getCurrentUserId()'),
    ]
    
    changed_files = []
    total_replacements = 0
    
    for file_path in html_files:
        # Пропускаем служебные файлы
        filename = os.path.basename(file_path)
        if any(skip in filename for skip in ['test-', 'ui-kit', 'navigation-component']):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_replacements = 0
        
        for pattern, replacement in patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"  🔍 Найдено {len(matches)} совпадений для паттерна: {pattern}")
                content = re.sub(pattern, replacement, content)
                file_replacements += len(matches)
        
        if content != original_content:
            print(f"📝 Исправление файла: {filename}")
            print(f"   Замен: {file_replacements}")
            
            # Создаем резервную копию
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Сохраняем исправленный файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            changed_files.append(filename)
            total_replacements += file_replacements
            print()
    
    print("🎉 ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!")
    print(f"📊 Статистика:")
    print(f"   Файлов изменено: {len(changed_files)}")
    print(f"   Всего замен: {total_replacements}")
    
    if changed_files:
        print(f"\n📁 Измененные файлы:")
        for filename in changed_files:
            print(f"   - {filename}")
        
        print(f"\n💾 Резервные копии созданы с расширением .backup")
        print(f"🔄 Перезапустите браузер для применения изменений")
    else:
        print("ℹ️ Не найдено файлов для исправления")

if __name__ == "__main__":
    print("🚀 Начинаем массовое исправление ссылок на user.id...")
    print("🎯 Заменяем user.id на Auth.getCurrentUserId()")
    print()
    
    fix_user_id_references()