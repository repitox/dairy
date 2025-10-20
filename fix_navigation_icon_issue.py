#!/usr/bin/env python3
"""
Скрипт для исправления проблемы с колонкой icon в навигации
Заменяет все упоминания icon в SQL запросах на корректные
"""
import os

def fix_navigation_file():
    """Исправляет файл manage_navigation.py на сервере"""
    
    # Читаем файл
    file_path = "app/manage_navigation.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📖 Читаем файл {file_path}")
        
        # Заменяем старые SQL запросы
        old_select_1 = """SELECT 
                        id, title, url, icon, description, 
                        sort_order, category, is_active, is_visible,"""
        
        new_select_1 = """SELECT 
                        id, title, url, description, 
                        sort_order, category, is_active, is_visible,"""
        
        old_select_2 = """SELECT title, url, icon, category, sort_order"""
        new_select_2 = """SELECT title, url, category, sort_order"""
        
        old_insert = """INSERT INTO navigation_items 
                    (title, url, icon, description, sort_order, category, is_active, is_visible)
                    VALUES (%s, %s, %s, %s, %s, %s, TRUE, TRUE)"""
        
        new_insert = """INSERT INTO navigation_items 
                    (title, url, description, sort_order, category, is_active, is_visible)
                    VALUES (%s, %s, %s, %s, %s, TRUE, TRUE)"""
        
        # Выполняем замены
        content = content.replace(old_select_1, new_select_1)
        content = content.replace(old_select_2, new_select_2)
        content = content.replace(old_insert, new_insert)
        
        # Убираем использование icon в коде
        content = content.replace("print(f\"{status} [{item['id']:2d}] {item['type']} {item['icon']} {item['title']}\")", 
                                "print(f\"{status} [{item['id']:2d}] {item['type']} {item['title']}\")")
        
        content = content.replace("print(f\"Иконка: {icon}\")", "# print(f\"Иконка: {icon}\")")
        
        # Убираем запрос иконки
        content = content.replace('icon = input("Иконка (emoji): ").strip()', 'icon = "•"  # Иконка по умолчанию')
        
        # Исправляем параметры в INSERT
        content = content.replace("(%s, %s, %s, %s, %s, %s, TRUE, TRUE)", "(%s, %s, %s, %s, %s, TRUE, TRUE)")
        content = content.replace("(title, url, icon, description, sort_order, category)", "(title, url, description, sort_order, category)")
        
        # Записываем исправленный файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Файл {file_path} исправлен")
        
    except Exception as e:
        print(f"❌ Ошибка при исправлении файла: {e}")

if __name__ == "__main__":
    fix_navigation_file()