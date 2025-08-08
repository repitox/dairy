#!/bin/bash

echo "📜 Получаем полный webapp-navigation-loader.js..."

sshpass -p 'YiKceHokjelen89' ssh -o StrictHostKeyChecking=no c107597@h60.netangels.ru << 'EOF'
cd dialist.ru/app

echo "📄 Полное содержимое webapp-navigation-loader.js:"
cat static/webapp-navigation-loader.js

EOF