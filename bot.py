import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, MenuButtonWebApp
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
import uvicorn

# === Конфигурация ===
TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")  # Например: https://your-bot.onrender.com
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

# === Telegram-приложение ===
telegram_app = ApplicationBuilder().token(TOKEN).build()

# === Обработчики ===

# Команда /start — опционально, может дублировать WebApp
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton(
            "Открыть WebApp",
            web_app=WebAppInfo(url=f"{RENDER_URL}/webapp")
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажми кнопку ниже:", reply_markup=reply_markup)

# (опционально) Обработка нажатий кнопок (если нужны)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'show_hello':
        await query.edit_message_text("Hello, World!")

# === Регистрация обработчиков ===
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

# === FastAPI-приложение ===
app = FastAPI()

# Получение обновлений от Telegram через Webhook
@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)

# Раздача HTML-файлов WebApp
app.mount("/webapp", StaticFiles(directory="static", html=True), name="webapp")

# Установка Webhook и меню при запуске
@app.on_event("startup")
async def on_startup():
    await telegram_app.initialize()

    # Удалим старый webhook и установим новый
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
    print(f"Webhook установлен: {WEBHOOK_URL}")

    # Установим WebApp-кнопку в меню Telegram
    await telegram_app.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Открыть WebApp",
            web_app=WebAppInfo(url=f"{RENDER_URL}/webapp")
        )
    )
    print("Кнопка WebApp добавлена в меню Telegram")