#!/usr/bin/env python3
"""
Утилита для настройки бота для работы с Login Widget
"""
import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

async def setup_bot():
    token = os.getenv("BOT_TOKEN")
    domain = os.getenv("DOMAIN", "https://rptx.na4u.ru")
    
    if not token:
        print("❌ BOT_TOKEN не найден в переменных окружения")
        return
    
    try:
        bot = Bot(token=token)
        me = await bot.get_me()
        
        print("🤖 Настройка бота для Login Widget:")
        print(f"   Бот: @{me.username}")
        print(f"   Домен: {domain}")
        print()
        
        print("📋 Инструкции по настройке:")
        print("1. Откройте чат с @BotFather в Telegram")
        print("2. Отправьте команду /setdomain")
        print(f"3. Выберите бота @{me.username}")
        print(f"4. Отправьте домен: {domain}")
        print()
        
        print("🔧 Дополнительные настройки (опционально):")
        print("• /setdescription - установить описание бота")
        print("• /setabouttext - установить текст 'О боте'")
        print("• /setuserpic - установить аватар бота")
        print()
        
        print("✅ После настройки домена Login Widget будет работать!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(setup_bot())