import os
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, MenuButtonWebApp, Bot
)
from fastapi_utils.tasks import repeat_every
from datetime import datetime, timedelta
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
from db import (
    init_db,
    add_user,
    add_purchase,
    get_purchases_by_status,
    update_purchase_status,
    add_event,
    update_event,
    deactivate_event,
    get_events_by_filter,
    get_conn,
    log_event
)
from db import update_user_timezone, get_user_timezone

# === Переехавшая функция напоминания о событиях ===
async def reminder_loop():
    while True:
        print("⏰ Фоновая задача reminder_loop сработала в", datetime.utcnow().isoformat())
        print("▶️ reminder_loop запущен")
        now = datetime.utcnow()
        check_time = now + timedelta(minutes=60)
        now_iso = now.isoformat()
        check_iso = check_time.isoformat()

        with get_conn() as conn:
            with conn.cursor() as cur:
                # События, которые стартуют через 60 минут (плюс/минус 1 минута)
                cur.execute("""
                    SELECT id, title, location, start_at
                    FROM events
                    WHERE active = TRUE
                    AND start_at BETWEEN %s AND %s
                """, (now_iso, check_iso))
                events = cur.fetchall()
                print(f"Найдено событий для напоминания: {len(events)}")

                cur.execute("SELECT user_id FROM users")
                print("▶️ Тестовая проверка. Список пользователей:")
                for row in cur.fetchall():
                    print("👤", row)
                cur.execute("SELECT user_id FROM users")
                users = [u[0] for u in cur.fetchall()]
                print(f"Пользователей для оповещения: {len(users)}")

        if not users:
            print("⚠️ Нет пользователей для отправки уведомлений.")
        if not events:
            print("⚠️ Нет подходящих событий для напоминания.")

        bot = Bot(token=TOKEN)

        for event in events:
            print(f"📣 Готовим уведомления для события: {event['title']} (start_at={event['start_at']})")
            start = datetime.fromisoformat(event["start_at"])
            formatted_time = start.strftime("%d.%m.%y %H:%M")

            for user_id in users:
                print(f"🔔 Пытаемся отправить пользователю {user_id} сообщение о событии {event['title']}")
                try:
                    await bot.send_message(
                        chat_id=user_id,
                        text=(
                            f"🔔 Напоминание\n"
                            f"📅 Скоро начнётся мероприятие:\n"
                            f"«{event['title']}»\n"
                            f"🕒 {formatted_time}\n"
                            f"📍 {event['location']}"
                        )
                    )
                    print(f"✅ Уведомление отправлено пользователю {user_id}")
                    log_event("reminder", f"Уведомление отправлено пользователю {user_id} о событии '{event['title']}'")
                except Exception as e:
                    print(f"❌ Ошибка при отправке пользователю {user_id}: {type(e).__name__} — {e}")
                    log_event("error", f"Ошибка при отправке пользователю {user_id}: {type(e).__name__} — {e}")
        await asyncio.sleep(60)
import uvicorn

# === Конфигурация ===
TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

telegram_app = ApplicationBuilder().token(TOKEN).build()

# === Обработчики Telegram ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(
        user_id=user.id,
        first_name=user.first_name or "",
        username=user.username or ""
    )

    keyboard = [[
        InlineKeyboardButton(
            "Открыть WebApp",
            web_app=WebAppInfo(url=f"{RENDER_URL}/webapp")
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажми кнопку ниже:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'show_hello':
        await query.edit_message_text("Hello, World!")


# === Новая команда для проверки уведомлений ===
async def test_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📩 test_notify вызван от:", update.effective_user.id)
    await update.message.reply_text("✅ Бот может отправлять тебе сообщения.")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))
telegram_app.add_handler(CommandHandler("test_notify", test_notify))

# === FastAPI-приложение ===
app = FastAPI()

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)

# === WebApp маршруты ===

app.mount("/webapp", StaticFiles(directory="static", html=True), name="webapp")

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

@app.put("/api/shopping/{purchase_id}")
async def update_status(purchase_id: int, request: Request):
    data = await request.json()
    new_status = data.get("status")

    if new_status not in ["Нужно купить", "Куплено", "Удалено"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    update_purchase_status(purchase_id, new_status)
    return {"status": "updated"}

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

@app.get("/api/events")
async def get_events(filter: str = "Предстоящие"):
    events = get_events_by_filter(filter)
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "location": r["location"],
            "start_at": r["start_at"],
            "end_at": r["end_at"],
            "active": bool(r["active"])  # Явно добавляем поле active
        } for r in events
    ]

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

@app.get("/api/user/timezone")
async def get_timezone(user_id: int):
    tz = get_user_timezone(user_id)
    return {"timezone": tz}

@app.post("/api/user/timezone")
async def set_timezone(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    timezone = data.get("timezone")
    if not user_id or not timezone:
        raise HTTPException(status_code=400, detail="Missing user_id or timezone")
    update_user_timezone(user_id, timezone)
    return {"status": "ok"}

# === Startup ===
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
    asyncio.create_task(reminder_loop())
    print(f"Webhook установлен: {WEBHOOK_URL}")
