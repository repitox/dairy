#!/bin/bash

echo "🌐 Проверяем что именно возвращает API навигации..."

sshpass -p 'YiKceHokjelen89' ssh -o StrictHostKeyChecking=no c107597@h60.netangels.ru << 'EOF'
cd dialist.ru/app

echo "📡 Прямой запрос к API:"
curl -s -X GET "http://localhost:8000/api/navigation?category=main"

echo ""
echo ""
echo "🔍 Проверяем статус сервера:"
ps aux | grep python3 | grep bot.py | grep -v grep

echo ""
echo "📝 Последние логи сервера:"
tail -n 10 nohup.out 2>/dev/null || echo "Файл nohup.out не найден"

EOF