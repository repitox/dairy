#!/bin/bash

echo "🐳 Запуск Telegram App в Docker..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker Desktop."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен."
    exit 1
fi

# Копируем переменные окружения
if [ ! -f .env ]; then
    echo "📋 Создаем .env файл..."
    cp .env.docker .env
fi

# Останавливаем существующие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker-compose down

# Собираем и запускаем
echo "🔨 Собираем образы..."
docker-compose build

echo "🚀 Запускаем контейнеры..."
docker-compose up -d

# Ждем запуска базы данных
echo "⏳ Ждем запуска базы данных..."
sleep 10

# Проверяем статус
echo "📊 Статус контейнеров:"
docker-compose ps

echo ""
echo "✅ Приложение запущено!"
echo "🌐 Основное приложение: http://localhost:8000"
echo "📱 Тест авторизации: http://localhost:8000/test-auth"
echo "🏠 Главная страница: http://localhost:8000/dashboard/"
echo "⚡ WebApp: http://localhost:8000/webapp/"
echo "🗄️ Adminer (БД): http://localhost:8080"
echo ""
echo "📋 Для остановки: ./docker-stop.sh"
echo "📋 Для просмотра логов: docker-compose logs -f"