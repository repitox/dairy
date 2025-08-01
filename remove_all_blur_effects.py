#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для полного удаления всех blur эффектов из CSS файла
Убирает backdrop-filter и -webkit-backdrop-filter из всех селекторов
"""

import os
import re

# Путь к CSS файлу
CSS_FILE = "/Users/d.dubenetskiy/Documents/tg_project/dashboard/ui-components.css"

def remove_blur_effects():
    """Удаляет все blur эффекты из CSS файла"""
    
    print("🔄 Удаление всех blur эффектов из ui-components.css")
    print("=" * 50)
    
    if not os.path.exists(CSS_FILE):
        print(f"❌ Файл не найден: {CSS_FILE}")
        return
    
    # Читаем файл
    try:
        with open(CSS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        print(f"📁 Размер файла: {original_size} символов")
        
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return
    
    # Создаем бэкап
    backup_path = CSS_FILE + '.backup-blur-removal'
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Создан бэкап: {backup_path}")
    except Exception as e:
        print(f"⚠️ Не удалось создать бэкап: {e}")
    
    # Подсчитываем количество blur эффектов
    backdrop_count = len(re.findall(r'backdrop-filter:\s*[^;/]+;', content))
    webkit_count = len(re.findall(r'-webkit-backdrop-filter:\s*[^;/]+;', content))
    
    print(f"🔍 Найдено backdrop-filter: {backdrop_count}")
    print(f"🔍 Найдено -webkit-backdrop-filter: {webkit_count}")
    
    if backdrop_count == 0 and webkit_count == 0:
        print("✅ Blur эффекты не найдены")
        return
    
    # Удаляем все backdrop-filter эффекты
    content = re.sub(
        r'backdrop-filter:\s*[^;]+;',
        '/* backdrop-filter removed */',
        content
    )
    
    # Удаляем все -webkit-backdrop-filter эффекты
    content = re.sub(
        r'-webkit-backdrop-filter:\s*[^;]+;',
        '/* -webkit-backdrop-filter removed */',
        content
    )
    
    # Удаляем blur() функции из других свойств
    content = re.sub(
        r'blur\([^)]+\)',
        '/* blur removed */',
        content
    )
    
    # Убираем лишние пустые строки
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Сохраняем обновленный файл
    try:
        with open(CSS_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        new_size = len(content)
        print(f"✅ Файл обновлен")
        print(f"📏 Новый размер: {new_size} символов")
        print(f"📊 Изменение размера: {new_size - original_size:+d} символов")
        
    except Exception as e:
        print(f"❌ Ошибка сохранения файла: {e}")
        return
    
    print(f"\n🎉 Все blur эффекты удалены!")
    print(f"✅ Удалено backdrop-filter: {backdrop_count}")
    print(f"✅ Удалено -webkit-backdrop-filter: {webkit_count}")
    print(f"💾 Бэкап сохранен: {backup_path}")

def verify_removal():
    """Проверяет, что все blur эффекты удалены"""
    
    print(f"\n🔍 Проверка удаления blur эффектов...")
    
    try:
        with open(CSS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем оставшиеся blur эффекты
        remaining_backdrop = re.findall(r'backdrop-filter:\s*(?!.*removed)[^;]+;', content)
        remaining_webkit = re.findall(r'-webkit-backdrop-filter:\s*(?!.*removed)[^;]+;', content)
        remaining_blur = re.findall(r'blur\([^)]+\)', content)
        
        if remaining_backdrop:
            print(f"⚠️ Найдены оставшиеся backdrop-filter:")
            for effect in remaining_backdrop[:5]:  # Показываем первые 5
                print(f"   • {effect}")
        
        if remaining_webkit:
            print(f"⚠️ Найдены оставшиеся -webkit-backdrop-filter:")
            for effect in remaining_webkit[:5]:
                print(f"   • {effect}")
        
        if remaining_blur:
            print(f"⚠️ Найдены оставшиеся blur():")
            for effect in remaining_blur[:5]:
                print(f"   • {effect}")
        
        if not remaining_backdrop and not remaining_webkit and not remaining_blur:
            print("✅ Все blur эффекты успешно удалены!")
        
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")

def main():
    """Основная функция"""
    
    remove_blur_effects()
    verify_removal()
    
    print(f"\n🧪 Для проверки:")
    print(f"   🌐 Откройте любую страницу dashboard")
    print(f"   🖱️ Наведите курсор на кнопки и ссылки")
    print(f"   👀 Проверьте отсутствие blur эффектов")

if __name__ == "__main__":
    main()