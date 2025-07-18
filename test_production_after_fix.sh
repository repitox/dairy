#!/bin/bash

# Тестирование API после исправления
echo "🧪 Тестирование API после исправления"
echo "====================================="

API_URL="https://rptx.na4u.ru"
USER_ID=1

# Тестирование endpoints
echo "📋 Тестирование основных endpoints:"

echo "🔍 Проекты..."
curl -s -X GET "$API_URL/api/projects?user_id=$USER_ID" | head -c 100
echo ""

echo "🔍 Задачи..."
curl -s -X GET "$API_URL/api/tasks?user_id=$USER_ID" | head -c 100
echo ""

echo "🔍 События..."
curl -s -X GET "$API_URL/api/events?user_id=$USER_ID" | head -c 100
echo ""

echo "🔍 Покупки..."
curl -s -X GET "$API_URL/api/shopping?user_id=$USER_ID" | head -c 100
echo ""

echo "🔍 Заметки..."
curl -s -X GET "$API_URL/api/notes?user_id=$USER_ID" | head -c 100
echo ""

echo "🔍 Настройки..."
curl -s -X GET "$API_URL/api/settings?user_id=$USER_ID" | head -c 100
echo ""

echo ""
echo "🧪 Тестирование создания данных:"

echo "📝 Создание заметки..."
curl -s -X POST "$API_URL/api/notes" \
  -H "Content-Type: application/json" \
  -d '{"title":"Тестовая заметка","content":"Автоматически созданная заметка","user_id":1}' | head -c 100
echo ""

echo "🛒 Создание покупки..."
curl -s -X POST "$API_URL/api/shopping" \
  -H "Content-Type: application/json" \
  -d '{"name":"Тестовая покупка","quantity":1,"price":99.99,"user_id":1}' | head -c 100
echo ""

echo ""
echo "📊 Проверка документации:"

echo "🔍 Документация API..."
curl -s -I "$API_URL/docs" | head -1
echo ""

echo "✅ Тестирование завершено!"
echo "🔍 Откройте: $API_URL/docs"