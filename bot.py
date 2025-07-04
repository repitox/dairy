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
from db import (
    get_shopping_items, add_shopping_item, toggle_shopping_item, delete_shopping_item,
    get_user_stats, get_dashboard_counters, toggle_task_status, delete_event_by_id, clear_user_data
)
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
    get_personal_project_id,
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
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")

@app.get("/test-auth")
async def test_auth():
    return FileResponse("test_auth.html")

@app.get("/local-auth")
async def local_auth():
    return FileResponse("local_auth.html")

@app.get("/api/shopping")
async def get_shopping(user_id: int):
    """Получить список покупок пользователя для dashboard"""
    try:
        items = get_shopping_items(user_id)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching shopping items: {str(e)}")

@app.post("/api/shopping")
async def add_to_shopping(request: Request):
    """Добавить новую покупку для dashboard"""
    data = await request.json()
    name = data.get("name")
    quantity = data.get("quantity", 1)
    price = data.get("price")
    category = data.get("category", "other")
    user_id = data.get("user_id")

    if not name or not user_id:
        raise HTTPException(status_code=400, detail="name and user_id required")

    try:
        item_id = add_shopping_item(user_id, name, int(quantity), price, category)
        return {"status": "ok", "id": item_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding shopping item: {str(e)}")

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

    if not all([title, location, start_at, end_at, user_id]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Если project_id = 'personal' или None, получаем ID личного проекта
    if project_id == 'personal' or project_id is None:
        project_id = get_personal_project_id(user_id)

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

# === User Timezone API ===
@app.get("/api/user/timezone")
async def get_user_timezone(user_id: int):
    """Получить часовой пояс пользователя"""
    try:
        timezone = get_user_setting(user_id, "timezone") or "0"
        return {"timezone": timezone}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting timezone: {str(e)}")

@app.post("/api/user/timezone")
async def set_user_timezone(request: Request):
    """Установить часовой пояс пользователя"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        timezone = data.get("timezone")
        
        if not user_id or timezone is None:
            raise HTTPException(status_code=400, detail="Missing user_id or timezone")
        
        # Валидируем часовой пояс (должен быть от -12 до +14)
        try:
            tz_offset = int(timezone)
            if tz_offset < -12 or tz_offset > 14:
                raise ValueError("Invalid timezone offset")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid timezone format")
        
        update_user_setting(user_id, "timezone", str(tz_offset))
        return {"status": "ok", "timezone": str(tz_offset)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting timezone: {str(e)}")

# === Dashboard Settings API ===
@app.get("/api/settings")
async def get_dashboard_settings(user_id: int):
    """Получить настройки dashboard пользователя"""
    try:
        print(f"🔍 Загрузка настроек для пользователя {user_id}")
        settings = get_user_settings(user_id)
        print(f"📊 Сырые настройки из БД: {settings}")
        
        if not isinstance(settings, dict):
            settings = {}
        
        # Конвертируем строки в правильные типы
        def str_to_bool(value, default=False):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return default
        
        result = {
            "theme": settings.get("theme", "auto"),
            "emailNotifications": str_to_bool(settings.get("email_notifications"), False),
            "taskReminders": str_to_bool(settings.get("task_reminders"), True)
        }
        
        print(f"✅ Отправляем настройки: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Ошибка загрузки настроек: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading settings: {str(e)}")

@app.post("/api/settings")
async def save_dashboard_settings(request: Request):
    """Сохранить настройки dashboard пользователя"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        print(f"🔧 Сохранение настроек для пользователя {user_id}: {data}")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user_id")
        
        # Сохраняем каждую настройку (конвертируем в строки)
        if "theme" in data:
            update_user_setting(user_id, "theme", str(data["theme"]))
            print(f"✅ Сохранена тема: {data['theme']}")
        
        if "email_notifications" in data:
            update_user_setting(user_id, "email_notifications", str(data["email_notifications"]).lower())
            print(f"✅ Сохранены email уведомления: {data['email_notifications']}")
        
        if "task_reminders" in data:
            update_user_setting(user_id, "task_reminders", str(data["task_reminders"]).lower())
            print(f"✅ Сохранены напоминания: {data['task_reminders']}")
        
        print("🎉 Все настройки сохранены успешно")
        return {"status": "ok"}
        
    except Exception as e:
        print(f"❌ Ошибка сохранения настроек: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving settings: {str(e)}")

@app.post("/api/clear-all-data")
async def clear_all_user_data(request: Request):
    """Очистить все данные пользователя"""
    data = await request.json()
    user_id = data.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")
    
    try:
        success = clear_user_data(user_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to clear user data")
        
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing data: {str(e)}")

# === Shopping API Extensions ===
@app.post("/api/shopping/{item_id}/toggle")
async def toggle_shopping_item_status(item_id: int, request: Request):
    """Переключить статус покупки"""
    data = await request.json()
    user_id = data.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")
    
    try:
        new_status = toggle_shopping_item(item_id, user_id)
        if new_status is None:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {"status": "ok", "completed": new_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling item: {str(e)}")

@app.delete("/api/shopping/{item_id}")
async def delete_shopping_item_endpoint(item_id: int):
    """Удалить покупку"""
    try:
        success = delete_shopping_item(item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting item: {str(e)}")

# === Tasks API Extensions ===
@app.post("/api/tasks/{task_id}/toggle")
async def toggle_task_status_endpoint(task_id: int, request: Request):
    """Переключить статус задачи"""
    data = await request.json()
    user_id = data.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")
    
    try:
        new_status = toggle_task_status(task_id, user_id)
        if new_status is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"status": "ok", "completed": new_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling task: {str(e)}")

@app.put("/api/tasks/{task_id}/complete")
async def complete_task_endpoint(task_id: int):
    """Завершить задачу (для совместимости со static)"""
    try:
        # Получаем задачу и завершаем её
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE tasks SET completed = TRUE WHERE id = %s", (task_id,))
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Task not found")
        
        return {"status": "ok", "completed": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing task: {str(e)}")

# === Events API Extensions ===
@app.delete("/api/events/{event_id}")
async def delete_event_endpoint(event_id: int):
    """Удалить событие"""
    try:
        success = delete_event_by_id(event_id)
        if not success:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting event: {str(e)}")

# === Dashboard Stats API ===
@app.get("/api/user-stats")
async def get_user_stats_endpoint(user_id: int):
    """Получить статистику пользователя для dashboard"""
    try:
        stats = get_user_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user stats: {str(e)}")

@app.get("/api/dashboard-counters")
async def get_dashboard_counters_endpoint(user_id: int):
    """Получить счетчики для навигации dashboard"""
    try:
        counters = get_dashboard_counters(user_id)
        return counters
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard counters: {str(e)}")

# === Telegram Auth endpoint ===
import hashlib
import hmac
from urllib.parse import unquote

def verify_telegram_auth(auth_data: dict, bot_token: str) -> bool:
    """Проверяет подлинность данных авторизации Telegram"""
    check_hash = auth_data.pop('hash', None)
    if not check_hash:
        return False
    
    # Создаем строку для проверки
    data_check_arr = []
    for key, value in sorted(auth_data.items()):
        if key != 'hash':
            data_check_arr.append(f"{key}={value}")
    
    data_check_string = '\n'.join(data_check_arr)
    
    # Создаем секретный ключ
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    
    # Вычисляем хеш
    calculated_hash = hmac.new(
        secret_key, 
        data_check_string.encode(), 
        hashlib.sha256
    ).hexdigest()
    
    return calculated_hash == check_hash

@app.post("/api/auth/telegram")
async def auth_telegram(request: Request):
    try:
        print("🔍 Получен запрос авторизации")
        data = await request.json()
        print(f"📝 Данные запроса: {data}")
        
        # Проверяем наличие необходимых данных
        if not data.get("hash"):
            print("❌ Отсутствует hash")
            raise HTTPException(status_code=400, detail="Missing hash")
        
        # Проверяем подпись (если включена проверка)
        # В продакшене обязательно включите эту проверку!
        verify_signature = os.getenv("VERIFY_TELEGRAM_SIGNATURE", "false").lower() == "true"
        print(f"🔐 Проверка подписи: {verify_signature}")
        
        if verify_signature:
            if not verify_telegram_auth(data.copy(), TOKEN):
                print("❌ Неверная подпись Telegram")
                raise HTTPException(status_code=401, detail="Invalid Telegram signature")
        
        # Извлекаем данные пользователя
        user_id = data.get("id")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        username = data.get("username", "")
        photo_url = data.get("photo_url", "")
        
        print(f"👤 Пользователь: ID={user_id}, Имя={first_name}, Username={username}")
        
        if not user_id:
            print("❌ Отсутствует user ID")
            raise HTTPException(status_code=400, detail="Missing user ID")
        
        # Добавляем пользователя в базу данных
        print("💾 Добавляем пользователя в БД...")
        add_user(user_id, first_name, username)
        print("✅ Пользователь добавлен")
        
        result = {
            "status": "ok", 
            "user": {
                "id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "photo_url": photo_url
            }
        }
        print(f"📤 Возвращаем результат: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 Неожиданная ошибка в auth_telegram: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# === Task API ===
from db import add_task, get_tasks, complete_task, get_personal_project_id
from typing import Optional

@app.get("/api/tasks")
async def api_get_tasks(user_id: int, project_id: Optional[int] = None):
    """Получить задачи пользователя с учетом часового пояса"""
    from datetime_utils import format_datetime_for_user, is_today, is_tomorrow, is_overdue
    
    # Получаем задачи из БД
    tasks = get_tasks(user_id, project_id)
    
    # Получаем часовой пояс пользователя
    user_timezone = get_user_setting(user_id, "timezone") or "0"
    
    # Обогащаем задачи информацией о датах
    enriched_tasks = []
    for task in tasks:
        task_dict = dict(task)
        
        if task_dict.get('due_date'):
            try:
                from datetime_utils import parse_datetime_string
                due_dt = parse_datetime_string(task_dict['due_date'])
                
                # Добавляем метаинформацию о дате
                task_dict['date_info'] = {
                    'is_today': is_today(due_dt, user_timezone),
                    'is_tomorrow': is_tomorrow(due_dt, user_timezone),
                    'is_overdue': is_overdue(due_dt, user_timezone),
                    'formatted_date': format_datetime_for_user(due_dt, user_timezone, 'relative'),
                    'formatted_full': format_datetime_for_user(due_dt, user_timezone, 'full')
                }
            except Exception as e:
                print(f"Ошибка обработки даты {task_dict['due_date']}: {e}")
                task_dict['date_info'] = None
        else:
            task_dict['date_info'] = None
            
        enriched_tasks.append(task_dict)
    
    return enriched_tasks

@app.get("/api/tasks/{task_id}")
async def api_get_task(task_id: int, user_id: int):
    """Получить одну задачу по ID"""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT t.id, t.title, t.description, t.due_date, t.priority,
                           t.completed, t.created_at, t.completed_at, t.project_id, 
                           p.name AS project_name, p.color AS project_color
                    FROM tasks t
                    LEFT JOIN projects p ON t.project_id = p.id
                    WHERE t.id = %s AND (t.user_id = %s OR t.project_id IN (
                        SELECT p2.id FROM projects p2 
                        WHERE p2.owner_id = %s OR p2.id IN (
                            SELECT pm.project_id FROM project_members pm WHERE pm.user_id = %s
                        )
                    ))
                """, (task_id, user_id, user_id, user_id))
                
                task = cur.fetchone()
                if not task:
                    raise HTTPException(status_code=404, detail="Task not found")
                
                return dict(task)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task: {str(e)}")

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
        raise HTTPException(status_code=400, detail="user_id and title required")

    # Если project_id = 'personal' или None, получаем ID личного проекта
    if project_id == 'personal' or project_id is None:
        project_id = get_personal_project_id(user_id)
    
    # Обрабатываем дату с учетом часового пояса пользователя
    processed_due_date = due_date
    if due_date:
        try:
            from datetime_utils import user_timezone_to_utc, parse_datetime_string
            user_timezone = get_user_setting(user_id, "timezone") or "0"
            
            # Если дата пришла от пользователя в его часовом поясе, конвертируем в UTC
            parsed_date = parse_datetime_string(due_date)
            if parsed_date:
                # Конвертируем в UTC для хранения в БД
                utc_date = user_timezone_to_utc(parsed_date, user_timezone)
                processed_due_date = utc_date.isoformat()
            
        except Exception as e:
            print(f"Ошибка обработки даты {due_date}: {e}")
            # Если не удалось обработать, используем как есть
            processed_due_date = due_date
    
    add_task(user_id, project_id, title, processed_due_date, priority, description)
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
    user_id = data.get("user_id")
    title = data.get("title")
    description = data.get("description", "")
    due_date = data.get("due_date")
    priority = data.get("priority", "обычная")

    if not user_id or not title:
        raise HTTPException(status_code=400, detail="user_id and title are required")

    with get_conn() as conn:
        with conn.cursor() as cur:
            # Проверяем, что задача принадлежит пользователю
            cur.execute("""
                SELECT id FROM tasks 
                WHERE id = %s AND (user_id = %s OR project_id IN (
                    SELECT p.id FROM projects p 
                    WHERE p.owner_id = %s OR p.id IN (
                        SELECT pm.project_id FROM project_members pm WHERE pm.user_id = %s
                    )
                ))
            """, (task_id, user_id, user_id, user_id))
            
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Task not found")
            
            # Обновляем задачу
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
async def api_delete_task(task_id: int, request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Проверяем, что задача принадлежит пользователю, и удаляем
            cur.execute("""
                DELETE FROM tasks 
                WHERE id = %s AND (user_id = %s OR project_id IN (
                    SELECT p.id FROM projects p 
                    WHERE p.owner_id = %s OR p.id IN (
                        SELECT pm.project_id FROM project_members pm WHERE pm.user_id = %s
                    )
                ))
            """, (task_id, user_id, user_id, user_id))
            
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Task not found")
            
            conn.commit()
    
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
    # Инициализация БД перенесена в start_server.py
    try:
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
            
    except Exception as e:
        print(f"⚠️ Ошибка инициализации Telegram: {e}")

@app.api_route("/ping", methods=["GET", "POST", "HEAD"])
async def ping():
    return {"status": "ok"}

@app.get("/dashboard", include_in_schema=False)
async def dashboard_entry():
    return FileResponse("dashboard/index.html")

from scheduler import start_scheduler
start_scheduler()