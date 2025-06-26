#!/usr/bin/env python3
"""
Утилита для получения информации о боте
"""
import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

async def get_bot_info():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN не найден в переменных окружения")
        return
    
    try:
        bot = Bot(token=token)
        me = await bot.get_me()
        
        print("🤖 Информация о боте:")
        print(f"   ID: {me.id}")
        print(f"   Username: @{me.username}")
        print(f"   Имя: {me.first_name}")
        print(f"   Может присоединяться к группам: {me.can_join_groups}")
        print(f"   Может читать все сообщения: {me.can_read_all_group_messages}")
        print(f"   Поддерживает inline: {me.supports_inline_queries}")
        
        print(f"\n📝 Для Telegram Login Widget используйте:")
        print(f"   data-telegram-login=\"{me.username}\"")
        
    except Exception as e:
        print(f"❌ Ошибка получения информации о боте: {e}")

if __name__ == "__main__":
    asyncio.run(get_bot_info())