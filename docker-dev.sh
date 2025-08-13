#!/bin/bash

# Скрипт для разработки с новой архитектурой

set -e

echo "🚀 Запуск среды разработки с новой архитектурой..."

# Функция для отображения помощи
show_help() {
    echo "Использование: $0 [КОМАНДА]"
    echo ""
    echo "Команды:"
    echo "  start     - Запустить все сервисы"
    echo "  stop      - Остановить все сервисы"
    echo "  restart   - Перезапустить сервисы"
    echo "  logs      - Показать логи"
    echo "  test      - Запустить тесты"
    echo "  shell     - Открыть shell в контейнере приложения"
    echo "  db-shell  - Открыть shell в БД"
    echo "  clean     - Очистить все данные"
    echo "  build     - Пересобрать образы"
    echo "  help      - Показать эту справку"
}

# Проверяем наличие docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose не найден. Установите Docker Compose."
    exit 1
fi

case "${1:-start}" in
    start)
        echo "🔧 Запуск сервисов..."
        docker-compose -f docker-compose.new.yml up -d app-new db adminer
        echo "✅ Сервисы запущены!"
        echo "📱 Новое приложение: http://localhost:8001"
        echo "🗄️  Adminer: http://localhost:8080"
        ;;
    
    stop)
        echo "🛑 Остановка сервисов..."
        docker-compose -f docker-compose.new.yml down
        echo "✅ Сервисы остановлены!"
        ;;
    
    restart)
        echo "🔄 Перезапуск сервисов..."
        docker-compose -f docker-compose.new.yml restart app-new
        echo "✅ Сервисы перезапущены!"
        ;;
    
    logs)
        echo "📋 Логи приложения:"
        docker-compose -f docker-compose.new.yml logs -f app-new
        ;;
    
    test)
        echo "🧪 Запуск тестов..."
        docker-compose -f docker-compose.new.yml --profile testing up --build test
        echo "✅ Тесты завершены!"
        ;;
    
    shell)
        echo "🐚 Открытие shell в контейнере..."
        docker-compose -f docker-compose.new.yml exec app-new bash
        ;;
    
    db-shell)
        echo "🗄️ Открытие shell в БД..."
        docker-compose -f docker-compose.new.yml exec db psql -U postgres -d telegram_app
        ;;
    
    clean)
        echo "🧹 Очистка данных..."
        docker-compose -f docker-compose.new.yml down -v
        docker system prune -f
        echo "✅ Данные очищены!"
        ;;
    
    build)
        echo "🔨 Пересборка образов..."
        docker-compose -f docker-compose.new.yml build --no-cache
        echo "✅ Образы пересобраны!"
        ;;
    
    help)
        show_help
        ;;
    
    *)
        echo "❌ Неизвестная команда: $1"
        show_help
        exit 1
        ;;
esac