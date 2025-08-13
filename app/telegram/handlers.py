"""
Обработчики Telegram команд
"""
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

from app.core.config import settings
from app.database.repositories.user_repository import user_repository


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    with open("/tmp/webhook_debug.log", "a") as f:
        f.write(f"⚡️ START HANDLER CALLED {datetime.utcnow().isoformat()}\n")
    
    print("⚡️ Обработчик /start вызван")
    user = update.effective_user
    print("👤 Пользователь:", user.id, user.username)
    
    with open("/tmp/webhook_debug.log", "a") as f:
        f.write(f"👤 User: ID={user.id}, username={user.username}, first_name={user.first_name}\n")
    
    try:
        result = user_repository.add_user(
            telegram_id=user.id,
            first_name=user.first_name or "",
            username=user.username or ""
        )
        with open("/tmp/webhook_debug.log", "a") as f:
            f.write(f"✅ add_user result: {result}\n")
            
    except Exception as e:
        with open("/tmp/webhook_debug.log", "a") as f:
            f.write(f"❌ add_user error: {e}\n")
        print(f"❌ Ошибка при добавлении пользователя: {e}")

    keyboard = [[
        InlineKeyboardButton(
            "Открыть WebApp",
            web_app=WebAppInfo(url=f"{settings.DOMAIN}/webapp")
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажми кнопку ниже:", reply_markup=reply_markup)
    
    with open("/tmp/webhook_debug.log", "a") as f:
        f.write(f"✅ START HANDLER COMPLETED\n\n")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()
    if query.data == 'show_hello':
        await query.edit_message_text("Hello, World!")


async def test_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая команда для проверки уведомлений"""
    print("📩 test_notify вызван от:", update.effective_user.id)
    await update.message.reply_text("✅ Бот может отправлять тебе сообщения.")


def setup_handlers(telegram_app):
    """Настройка обработчиков команд"""
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(button_handler))
    telegram_app.add_handler(CommandHandler("test_notify", test_notify))