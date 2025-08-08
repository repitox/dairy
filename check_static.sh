#!/bin/bash

echo "📁 Проверяем статические файлы WebApp..."

sshpass -p 'YiKceHokjelen89' ssh -o StrictHostKeyChecking=no c107597@h60.netangels.ru << 'EOF'
cd dialist.ru/app

echo "📂 Структура папки static:"
ls -la static/ 2>/dev/null || echo "Папка static не найдена"

echo ""
echo "📄 Проверяем index.html в static:"
if [ -f "static/index.html" ]; then
    echo "✅ static/index.html существует"
    echo "🔍 Ищем навигацию в index.html:"
    grep -n -A 5 -B 5 "navigation\|nav\|menu" static/index.html | head -20
else
    echo "❌ static/index.html не найден"
fi

echo ""
echo "📄 Проверяем основные HTML файлы:"
find static/ -name "*.html" -type f 2>/dev/null | head -10

EOF