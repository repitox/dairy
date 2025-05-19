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
from fastapi import HTTPException
from db import (
    add_purchase,
    get_purchases_by_status,
    update_purchase_status
)

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
        [InlineKeyboardButton("Админка", web_app=WebAppInfo(url=f"{RENDER_URL}/webapp/admin/index.html"))]
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

@app.post("/api/shopping")
async def add_to_shopping(request: Request):
    data = await request.json()
    item = data.get("item")
    quantity = data.get("quantity")
    user_id = data.get("user_id")

    if not item or not quantity:
        raise HTTPException(status_code=400, detail="item and quantity required")

    add_purchase(user_id, item, int(quantity))
    return {"status": "ok"}

@app.get("/api/shopping")
async def get_shopping(status: str = "Нужно купить"):
    rows = get_purchases_by_status(status)
    return [
    {
        "id": r["id"],
        "item": r["item"],
        "quantity": r["quantity"],
        "status": r["status"],
        "created_at": r["created_at"]
    } for r in rows
]

@app.put("/api/shopping/{purchase_id}")
async def update_status(purchase_id: int, request: Request):
    data = await request.json()
    new_status = data.get("status")

    if new_status not in ["Нужно купить", "Куплено", "Удалено"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    update_purchase_status(purchase_id, new_status)
    return {"status": "updated"}

@app.get("/api/tables")
async def get_all_tables():
    import psycopg2
    from os import getenv

    DATABASE_URL = getenv("DATABASE_URL")
    result = {}

    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            # Получаем список таблиц
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = [row[0] for row in cur.fetchall()]

            for table in tables:
                cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table,))
                columns = [col[0] for col in cur.fetchall()]

                cur.execute(f"SELECT * FROM {table} LIMIT 20")
                rows = cur.fetchall()

                result[table] = {
                    "columns": columns,
                    "rows": rows
                }

    return result

from db import (
    add_event,
    get_active_events,
    update_event,
    deactivate_event,
    get_conn
)
from fastapi import HTTPException

@app.post("/api/events")
async def create_event(request: Request):
    data = await request.json()
    title = data.get("title")
    location = data.get("location")
    start_at = data.get("start_at")
    end_at = data.get("end_at")

    if not all([title, location, start_at, end_at]):
        raise HTTPException(status_code=400, detail="Missing fields")

    add_event(title, location, start_at, end_at)
    return {"status": "ok"}

from datetime import datetime

@app.get("/api/events")
async def get_events(filter: str = "Активные"):
    with get_conn() as conn:
        with conn.cursor() as cur:
            now = datetime.utcnow().isoformat()

            if filter == "Все":
                cur.execute("""
                    SELECT id, title, location, start_at, end_at
                    FROM events
                    WHERE active = TRUE OR active = FALSE
                    ORDER BY start_at ASC
                """)
            elif filter == "Прошедшие":
                cur.execute("""
                    SELECT id, title, location, start_at, end_at
                    FROM events
                    WHERE active = TRUE AND end_at < %s
                    ORDER BY start_at ASC
                """, (now,))
            else:  # Активные
                cur.execute("""
                    SELECT id, title, location, start_at, end_at
                    FROM events
                    WHERE active = TRUE AND end_at >= %s
                    ORDER BY start_at ASC
                """, (now,))

            return cur.fetchall()

@app.put("/api/events/{event_id}")
async def edit_event(event_id: int, request: Request):
    data = await request.json()
    title = data.get("title")
    location = data.get("location")
    start_at = data.get("start_at")
    end_at = data.get("end_at")

    if not all([title, location, start_at, end_at]):
        raise HTTPException(status_code=400, detail="Missing fields")

    update_event(event_id, title, location, start_at, end_at)
    return {"status": "updated"}

@app.put("/api/events/{event_id}/deactivate")
async def deactivate_event_api(event_id: int):
    deactivate_event(event_id)
    return {"status": "deactivated"}