#!/bin/bash

echo "📜 Получаем функцию toggleNavigationMenu из event_create.html..."

sshpass -p 'YiKceHokjelen89' ssh -o StrictHostKeyChecking=no c107597@h60.netangels.ru << 'EOF'
cd dialist.ru/app

echo "📄 Функция toggleNavigationMenu из event_create.html:"
grep -A 30 "function toggleNavigationMenu" static/event_create.html

EOF