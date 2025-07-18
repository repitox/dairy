#!/bin/bash

# Автоматизированный скрипт для исправления продакшена
echo "🚀 Исправление продакшена..."

# Создание SQL скрипта
cat > fix_db.sql << 'EOF'
-- Создаем таблицу notes
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Добавляем колонки в purchases
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'purchases' AND column_name = 'shopping_list_id') THEN
        ALTER TABLE purchases ADD COLUMN shopping_list_id INTEGER;
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'purchases' AND column_name = 'url') THEN
        ALTER TABLE purchases ADD COLUMN url TEXT;
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'purchases' AND column_name = 'comment') THEN
        ALTER TABLE purchases ADD COLUMN comment TEXT;
    END IF;
END $$;

-- Создаем таблицу users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создаем тестового пользователя
INSERT INTO users (id, name, email) 
VALUES (1, 'Test User', 'test@example.com')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, email = EXCLUDED.email;

-- Создаем тестовую заметку
INSERT INTO notes (title, content, user_id) 
VALUES ('Тестовая заметка', 'Содержимое тестовой заметки', 1);

SELECT 'База данных обновлена!' as status;
EOF

# Выполнение SQL
echo "📋 Обновление базы данных..."
PGPASSWORD="ZiKceXoydixol93" psql -h postgres.c107597.h2 -U c107597_rptx_na4u_ru -d c107597_rptx_na4u_ru -f fix_db.sql

# Перезапуск приложения
echo "🔄 Перезапуск приложения..."
pkill -f python
sleep 3

# Запуск приложения
if [ -f "app.py" ]; then
    nohup python3 app.py > app.log 2>&1 &
elif [ -f "main.py" ]; then
    nohup python3 main.py > app.log 2>&1 &
fi

echo "✅ Готово!"
echo "🔍 Проверьте: https://rptx.na4u.ru/docs"

# Очистка
rm -f fix_db.sql