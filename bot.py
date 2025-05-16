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
from db import init_db, add_user
from db import get_all_users  # создадим сейчас
from fastapi.responses import JSONResponse

# === Конфигурация ===
TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

# === Telegram-приложение ===
telegram_app = ApplicationBuilder().token(TOKEN).build()

# Обработчик /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(
        user_id=user.id,
        first_name=user.first_name or "",
        username=user.username or ""
    )

    keyboard = [
        [InlineKeyboardButton("Открыть WebApp",web_app=WebAppInfo(url=f"{RENDER_URL}/webapp"))],
        [InlineKeyboardButton("Админка", web_app=WebAppInfo(url=f"{RENDER_URL}/webapp/admin-index.html"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# Обработка inline кнопок (опционально)
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

# Обработка Webhook
@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)

# Раздача HTML-файлов WebApp
app.mount("/webapp", StaticFiles(directory="static", html=True), name="webapp")

@app.get("/api/users")
async def get_users_api():
    users = get_all_users()
    return JSONResponse(content=users)

# При запуске: инициализация базы, Webhook, меню
@app.on_event("startup")
async def on_startup():
    init_db()
    await telegram_app.initialize()
    await telegram_app.bot.delete_webhook()
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)

    await telegram_app.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Открыть WebApp",
            web_app=WebAppInfo(url=f"{RENDER_URL}/webapp")
        )
    )
    print(f"Webhook установлен: {WEBHOOK_URL}")