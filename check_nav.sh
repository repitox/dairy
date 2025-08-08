#!/bin/bash

# Проверка навигации на продакшене
echo "🔍 Проверяем навигацию на продакшене..."

# Подключаемся и проверяем БД
sshpass -p 'YiKceHokjelen89' ssh -o StrictHostKeyChecking=no c107597@h60.netangels.ru << 'EOF'
cd dialist.ru/app

echo "📊 Проверяем таблицу navigation_items в БД..."

python3 -c "
import psycopg2

try:
    conn = psycopg2.connect(
        host='postgres.c107597.h2',
        database='c107597_dialist_ru', 
        user='c107597_dialist_ru',
        password='ZoXboBiphobem19',
        port=5432
    )
    
    cursor = conn.cursor()
    
    # Проверяем записи навигации
    cursor.execute('''
        SELECT id, title, url, icon, is_active, is_visible
        FROM navigation_items 
        ORDER BY sort_order ASC, title ASC;
    ''')
    rows = cursor.fetchall()
    
    print(f'📋 Всего записей в navigation_items: {len(rows)}')
    print('=' * 60)
    
    active_count = 0
    for row in rows:
        status = '✅' if (row[4] and row[5]) else '❌'
        if row[4] and row[5]:
            active_count += 1
        print(f'ID: {row[0]:2} | {row[1]:15} | {status}')
    
    print(f'\\n🟢 Активных записей: {active_count}')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Ошибка БД: {e}')
"

echo ""
echo "🌐 Тестируем API навигации..."
curl -s -X GET "http://localhost:8000/api/navigation?category=main" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'📊 API вернул {len(data.get(\"navigation\", []))} пунктов навигации')
    for item in data.get('navigation', []):
        print(f'  - {item.get(\"title\", \"\")} ({item.get(\"url\", \"\")})')
except:
    print('❌ Ошибка парсинга ответа API')
"

EOF