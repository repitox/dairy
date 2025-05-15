from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
import os
from fastapi import FastAPI, Request
import uvicorn

TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

# --- Telegram-приложение ---
telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start := lambda u, c: u.message.reply_text("Нажми кнопку ниже:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Показать Hello World", callback_data='show_hello')]]))))
telegram_app.add_handler(CallbackQueryHandler(button_handler := lambda u, c: u.callback_query.edit_message_text("Hello, World!") if u.callback_query.data == 'show_hello' else None))

# --- FastAPI-приложение ---
app = FastAPI()

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)

@app.on_event("startup")
async def on_startup():
    await telegram_app.initialize()
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
    print(f"Webhook установлен: {WEBHOOK_URL}")