#!/bin/bash

echo "🔍 Ищем функцию toggleNavigationMenu..."

sshpass -p 'YiKceHokjelen89' ssh -o StrictHostKeyChecking=no c107597@h60.netangels.ru << 'EOF'
cd dialist.ru/app

echo "📜 Поиск toggleNavigationMenu во всех JS файлах:"
grep -r "toggleNavigationMenu" static/ --include="*.js" || echo "Функция не найдена в JS файлах"

echo ""
echo "📄 Поиск toggleNavigationMenu во всех HTML файлах:"
grep -r "toggleNavigationMenu" static/ --include="*.html" | head -5

echo ""
echo "🔍 Проверяем webapp-styles.css на наличие стилей для навигации:"
grep -n -A 5 -B 5 "navigation\|nav-menu\|hamburger" static/webapp-styles.css | head -20

EOF