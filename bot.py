import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
import uvicorn

# === Переменные окружения ===
TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

# === Telegram-приложение ===
telegram_app = ApplicationBuilder().token(TOKEN).build()

# Команда /start с кнопкой WebApp
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton(
            "Открыть WebApp",
            web_app=WebAppInfo(url=f"{RENDER_URL}/webapp")
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажми кнопку ниже:", reply_markup=reply_markup)

# (Опционально) обработка inline-кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'show_hello':
        await query.edit_message_text("Hello, World!")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

# === FastAPI-приложение ===
app = FastAPI()

# Обработка Webhook
@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)

# Раздача WebApp HTML из папки static/
app.mount("/webapp", StaticFiles(directory="static", html=True), name="webapp")

# Установка Webhook при запуске
@app.on_event("startup")
async def on_startup():
    await telegram_app.initialize()
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
    print(f"Webhook установлен: {WEBHOOK_URL}")