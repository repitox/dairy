#!/bin/bash

echo "📄 Проверяем навигационную структуру в index.html..."

sshpass -p 'YiKceHokjelen89' ssh -o StrictHostKeyChecking=no c107597@h60.netangels.ru << 'EOF'
cd dialist.ru/app

echo "🔍 Ищем навигационное меню в index.html:"
grep -n -A 10 -B 5 "navigation-menu\|menu-overlay" static/index.html

echo ""
echo "🔍 Ищем гамбургер кнопку:"
grep -n -A 5 -B 5 "hamburger-menu" static/index.html

echo ""
echo "🔍 Ищем JavaScript функции в index.html:"
grep -n -A 10 -B 5 "function\|<script>" static/index.html | tail -20

EOF