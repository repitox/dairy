"""
Настройка Telegram бота
"""
from telegram.ext import ApplicationBuilder
from app.core.config import settings
from app.telegram.handlers import setup_handlers
from app.telegram.reminders import reminder_loop


def setup_telegram_app():
    """Настройка Telegram приложения"""
    telegram_app = ApplicationBuilder().token(settings.BOT_TOKEN).build()
    setup_handlers(telegram_app)
    return telegram_app


async def start_reminder_loop():
    """Запуск цикла напоминаний"""
    await reminder_loop()