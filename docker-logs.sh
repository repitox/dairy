#!/bin/bash

echo "📋 Просмотр логов Telegram App..."

# Показываем логи всех сервисов
docker-compose logs -f --tail=100