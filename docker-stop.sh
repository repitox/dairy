#!/bin/bash

echo "🛑 Остановка Telegram App..."

# Останавливаем контейнеры
docker-compose down

echo "✅ Все контейнеры остановлены!"

# Опционально: удаляем образы
read -p "🗑️ Удалить образы? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ Удаляем образы..."
    docker-compose down --rmi all --volumes --remove-orphans
    echo "✅ Образы удалены!"
fi