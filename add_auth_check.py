#!/usr/bin/env python3
"""
Скрипт для добавления проверки регистрации во все страницы WebApp
"""
import os
import re

# Список страниц, которые нужно обновить (исключаем admin и старые файлы)
PAGES_TO_UPDATE = [
    'events.html',
    'project.html', 
    'task.html',
    'project_create.html',
    'task_add.html',
    'shopping.html',
    'event_create.html',
    'project_select.html',
    'task_edit.html',
    'settings.html',
    'timezone-settings.html'
]

STATIC_DIR = '/app/static'

def add_auth_script(file_path):
    """Добавить auth-check.js в HTML файл"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, есть ли уже auth-check.js
    if 'auth-check.js' in content:
        print(f"✅ {os.path.basename(file_path)} - auth-check.js уже добавлен")
        return False
    
    # Ищем место для вставки скрипта (после telegram-web-app.js)
    pattern = r'(<script src="https://telegram\.org/js/telegram-web-app\.js"></script>)'
    replacement = r'\1\n    <script src="auth-check.js"></script>'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ {os.path.basename(file_path)} - добавлен auth-check.js")
        return True
    else:
        print(f"⚠️ {os.path.basename(file_path)} - не найден telegram-web-app.js")
        return False

def wrap_dom_content_loaded(file_path):
    """Обернуть DOMContentLoaded в проверку регистрации"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, есть ли уже AuthCheck.initAuthCheck
    if 'AuthCheck.initAuthCheck' in content:
        print(f"✅ {os.path.basename(file_path)} - AuthCheck уже добавлен")
        return False
    
    # Ищем простые случаи DOMContentLoaded
    patterns = [
        # Случай 1: document.addEventListener('DOMContentLoaded', function() { ... });
        (
            r"document\.addEventListener\('DOMContentLoaded',\s*function\(\)\s*\{\s*\n(.*?)\n\s*\}\);",
            lambda m: f"""document.addEventListener('DOMContentLoaded', function() {{
      // Проверяем регистрацию пользователя
      AuthCheck.initAuthCheck(
        // Callback для зарегистрированного пользователя
        (userId) => {{
          console.log("Пользователь зарегистрирован");
{m.group(1)}
        }},
        // Callback для незарегистрированного пользователя
        () => {{
          console.log("Пользователь не зарегистрирован");
        }}
      );
    }});"""
        ),
        # Случай 2: document.addEventListener("DOMContentLoaded", () => { ... });
        (
            r"document\.addEventListener\(\"DOMContentLoaded\",\s*\(\)\s*=>\s*\{\s*\n(.*?)\n\s*\}\);",
            lambda m: f"""document.addEventListener("DOMContentLoaded", () => {{
      // Проверяем регистрацию пользователя
      AuthCheck.initAuthCheck(
        // Callback для зарегистрированного пользователя
        (userId) => {{
          console.log("Пользователь зарегистрирован");
{m.group(1)}
        }},
        // Callback для незарегистрированного пользователя
        () => {{
          console.log("Пользователь не зарегистрирован");
        }}
      );
    }});"""
        )
    ]
    
    modified = False
    for pattern, replacement_func in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            new_content = re.sub(pattern, replacement_func(match), content, flags=re.DOTALL)
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ {os.path.basename(file_path)} - обновлен DOMContentLoaded")
                modified = True
                break
    
    if not modified:
        print(f"⚠️ {os.path.basename(file_path)} - не найден подходящий DOMContentLoaded")
    
    return modified

def main():
    print("🚀 Добавление проверки регистрации в WebApp страницы...")
    
    updated_files = []
    
    for page in PAGES_TO_UPDATE:
        file_path = os.path.join(STATIC_DIR, page)
        
        if not os.path.exists(file_path):
            print(f"❌ {page} - файл не найден")
            continue
        
        print(f"\n📄 Обрабатываем {page}...")
        
        # Добавляем скрипт auth-check.js
        script_added = add_auth_script(file_path)
        
        # Оборачиваем DOMContentLoaded
        dom_updated = wrap_dom_content_loaded(file_path)
        
        if script_added or dom_updated:
            updated_files.append(page)
    
    print(f"\n✨ Обновлено файлов: {len(updated_files)}")
    for file in updated_files:
        print(f"  - {file}")
    
    print("\n🎯 Проверка регистрации добавлена во все основные страницы WebApp!")

if __name__ == "__main__":
    main()