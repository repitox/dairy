#!/bin/bash

echo "📜 Проверяем webapp-navigation-loader.js..."

sshpass -p 'YiKceHokjelen89' ssh -o StrictHostKeyChecking=no c107597@h60.netangels.ru << 'EOF'
cd dialist.ru/app

echo "📄 Содержимое webapp-navigation-loader.js:"
head -50 static/webapp-navigation-loader.js

echo ""
echo "🔍 Ищем функцию toggleNavigationMenu:"
grep -n -A 10 -B 5 "toggleNavigationMenu" static/webapp-navigation-loader.js

echo ""
echo "🔍 Ищем загрузку навигации из API:"
grep -n -A 5 -B 5 "api/navigation" static/webapp-navigation-loader.js

EOF