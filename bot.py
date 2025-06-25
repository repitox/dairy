import os
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import Optional
from fastapi.responses import FileResponse, RedirectResponse

from db import create_project
from db import update_user_setting, get_user_settings, get_user_setting
from db import get_today_events, get_recent_purchases, get_today_tasks
from dotenv import load_dotenv
load_dotenv()  # загрузит переменные из .env

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
    log_event,
    has_reminder_been_sent,
    record_reminder_sent,
)

# Импорт для нового маршрута /api/events (GET)
from db import get_user_events
from db import add_project_member, get_project

TOKEN = os.getenv("BOT_TOKEN")

# === Переехавшая функция напоминания о событиях  ===
async def reminder_loop():
    while True:
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

                cur.execute("SELECT user_id FROM users")
                users = [u["user_id"] for u in cur.fetchall()]

        if not users:
            log_event("info", "Нет пользователей для отправки уведомлений.")
        if not events:
            log_event("info", "Нет подходящих событий для напоминания.")

        bot = Bot(token=TOKEN)

        for event in events:
            for user_id in users:
                if has_reminder_been_sent(user_id, event["id"]):
                    continue

                start = datetime.fromisoformat(event["start_at"])
                user_tz_offset = get_user_setting(user_id, "timezone") or "0"

                try:
                    offset_hours = int(user_tz_offset)
                except ValueError:
                    offset_hours = 0

                user_time = start + timedelta(hours=offset_hours)
                formatted_time = user_time.strftime("%d.%m.%y %H:%M")

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
                    log_event("reminder", f"Уведомление отправлено пользователю {user_id} о событии '{event['title']}'")
                    record_reminder_sent(user_id, event["id"])
                except Exception as e:
                    log_event("error", f"Ошибка при отправке пользователю {user_id}: {type(e).__name__} — {e}")
        await asyncio.sleep(60)
import uvicorn

# === Конфигурация ===
# TOKEN = os.getenv("BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN", "https://rptx.na4u.ru")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{DOMAIN}{WEBHOOK_PATH}"

telegram_app = ApplicationBuilder().token(TOKEN).build()

# === Обработчики Telegram ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("⚡️ Обработчик /start вызван")
    user = update.effective_user
    print("👤 Пользователь:", user.id, user.username)
    add_user(
        user_id=user.id,
        first_name=user.first_name or "",
        username=user.username or ""
    )

    keyboard = [[
        InlineKeyboardButton(
            "Открыть WebApp",
            web_app=WebAppInfo(url=f"{DOMAIN}/webapp")
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
    print("📩 Webhook получен:", data.get("message", data))
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)

# === WebApp маршруты ===

app.mount("/webapp", StaticFiles(directory="static", html=True), name="webapp")
app.mount("/dashboard", StaticFiles(directory="dashboard"), name="dashboard")

@app.get("/api/shopping")
async def get_shopping(user_id: int, project_id: int, status: str = "Нужно купить"):
    rows = get_purchases_by_status(status, project_id)
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
    project_id = data.get("project_id")

    if not item or not quantity or not project_id:
        raise HTTPException(status_code=400, detail="item, quantity, and project_id required")

    add_purchase(user_id, project_id, item, int(quantity))
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
    user_id = data.get("user_id")
    project_id = data.get("project_id")

    if not all([title, location, start_at, end_at, user_id, project_id]):
        raise HTTPException(status_code=400, detail="Missing fields")

    add_event(user_id, project_id, title, location, start_at, end_at)
    return {"status": "ok"}

@app.get("/api/events")
async def get_events(user_id: int, filter: str = "Предстоящие"):
    events = get_user_events(user_id, filter)
    return events

@app.put("/api/events/{event_id}")
async def edit_event(event_id: int, request: Request):
    data = await request.json()
    title = data.get("title")
    location = data.get("location")
    start_at = data.get("start_at")
    end_at = data.get("end_at")
    user_id = data.get("user_id")

    if not all([title, location, start_at, end_at, user_id]):
        raise HTTPException(status_code=400, detail="Missing fields")

    update_event(event_id, user_id, title, location, start_at, end_at)
    return {"status": "updated"}

@app.put("/api/events/{event_id}/deactivate")
async def deactivate_event_api(event_id: int):
    deactivate_event(event_id)
    return {"status": "deactivated"}


# === Универсальный API endpoint для работы с настройками пользователя ===
@app.get("/api/user/settings")
async def get_user_settings_api(user_id: int):
    settings = get_user_settings(user_id)
    if not isinstance(settings, dict):
        raise HTTPException(status_code=500, detail="Settings not loaded correctly")
    return {
        "theme": settings.get("theme", "auto")
    }

@app.post("/api/user/settings")
async def set_user_settings(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    theme = data.get("theme")

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")

    if theme is not None:
        update_user_setting(user_id, "theme", theme)

    return {"status": "ok"}

# === Task API ===
from db import add_task, get_tasks, complete_task
from typing import Optional

@app.get("/api/tasks")
async def api_get_tasks(user_id: int, project_id: Optional[int] = None):
    return get_tasks(user_id, project_id)

@app.post("/api/tasks")
async def api_add_task(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    project_id = data.get("project_id")
    title = data.get("title")
    description = data.get("description", "")
    priority = data.get("priority", "обычная")
    due_date = data.get("due_date")

    if not user_id or not title:
        raise HTTPException(status_code=400, detail="user_id, project_id and title required")

    add_task(user_id, project_id, title, due_date, priority, description)
    return {"status": "ok"}


@app.put("/api/tasks/{task_id}/complete")
async def api_complete_task(task_id: int):
    complete_task(task_id)
    return {"status": "completed"}

# === API-маршрут редактирования задачи по ID ===
from datetime import datetime

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: int, request: Request):
    data = await request.json()
    title = data.get("title")
    description = data.get("description", "")
    date = data.get("date")
    time = data.get("time")
    priority = data.get("priority", "обычная")

    if not title:
        raise HTTPException(status_code=400, detail="Title is required")

    due_date = None
    if date and time:
        try:
            due_date = datetime.fromisoformat(f"{date}T{time}").isoformat()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid date/time format")
    elif date:
        due_date = date

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tasks
                SET title = %s,
                    description = %s,
                    due_date = %s,
                    priority = %s
                WHERE id = %s
            """, (title, description, due_date, priority, task_id))
            conn.commit()

    return {"status": "updated"}

# === API-маршрут удаления задачи по ID ===
from db import delete_task  # убедись, что импорт включен

@app.delete("/api/tasks/{task_id}")
async def api_delete_task(task_id: int):
    delete_task(task_id)
    return {"status": "deleted"}

# === Today endpoints ===

@app.get("/api/tasks/today")
async def api_today_tasks(user_id: int):
    result = get_today_tasks(user_id)
    return {
        "overdue": result.get("overdue", []),
        "today": result.get("today", [])
    }

@app.get("/api/events/today")
async def api_today_events(user_id: int):
    return get_today_events(user_id)

@app.get("/api/shopping/today")
async def api_recent_purchases(user_id: int):
    return get_recent_purchases(user_id)


# === Projects endpoints ===

# Удалены /api/projects GET и POST, добавлен create_project_api:

from db import get_user_projects

@app.get("/api/project/list")
async def list_user_projects(user_id: int):
    return get_user_projects(user_id)

@app.post("/api/project/create")
async def create_project_api(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    name = data.get("name")
    color = data.get("color", "#4f46e5")  # значение по умолчанию

    if not user_id or not name:
        raise HTTPException(status_code=400, detail="Missing fields")

    project_id = create_project(name, user_id, color)
    return {"id": project_id}

@app.get("/api/project")
async def get_project_info(id: int):
    project = get_project(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"id": project["id"], "name": project["name"]}

@app.post("/api/project/invite")
async def invite_user_to_project(request: Request):
    data = await request.json()
    project_id = data.get("project_id")
    user_id = data.get("user_id")
    if not project_id or not user_id:
        raise HTTPException(status_code=400, detail="Missing fields")
    add_project_member(project_id, user_id)
    return {"status": "ok"}

# === Startup ===
@app.on_event("startup")
async def on_startup():
    init_db()
    await telegram_app.initialize()
    await telegram_app.bot.delete_webhook()

    await telegram_app.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Открыть WebApp",
            web_app=WebAppInfo(url=f"{DOMAIN}/webapp")
        )
    )
    asyncio.create_task(reminder_loop())
    print(f"Webhook установлен: {WEBHOOK_URL}")
    try:
        await telegram_app.bot.send_message(
            chat_id=88504731,  # ← замени на нужный user_id
            text="🤖 Бот был успешно перезапущен и готов к работе!"
        )
        print("✅ Сообщение о старте отправлено.")
    except Exception as e:
        print("❌ Ошибка при отправке сообщения о старте:", e)

@app.api_route("/ping", methods=["GET", "POST", "HEAD"])
async def ping():
    return {"status": "ok"}

@app.get("/dashboard", include_in_schema=False)
async def dashboard_entry():
    return FileResponse("dashboard/index.html")

from scheduler import start_scheduler
start_scheduler()