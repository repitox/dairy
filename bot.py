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
    get_shopping_items, add_shopping_item, toggle_shopping_item, delete_shopping_item, update_shopping_item,
    get_user_shopping_lists, create_shopping_list, get_shopping_list, update_shopping_list, 
    delete_shopping_list, get_shopping_items_by_lists,
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
    get_user_personal_project_id,
    record_reminder_sent,
    update_shopping_item,
    resolve_user_id,
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

                cur.execute("SELECT telegram_id FROM users")
                users = [u["telegram_id"] for u in cur.fetchall()]

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
DOMAIN = os.getenv("DOMAIN", "https://dialist.ru")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{DOMAIN}{WEBHOOK_PATH}"

telegram_app = ApplicationBuilder().token(TOKEN).build()

# === Обработчики Telegram ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("/tmp/webhook_debug.log", "a") as f:
        f.write(f"⚡️ START HANDLER CALLED {datetime.utcnow().isoformat()}\n")
    
    print("⚡️ Обработчик /start вызван")
    user = update.effective_user
    print("👤 Пользователь:", user.id, user.username)
    
    with open("/tmp/webhook_debug.log", "a") as f:
        f.write(f"👤 User: ID={user.id}, username={user.username}, first_name={user.first_name}\n")
    
    try:
        # Проверяем DATABASE_URL перед добавлением пользователя
        db_url = os.getenv("DATABASE_URL", "НЕ УСТАНОВЛЕН")
        with open("/tmp/webhook_debug.log", "a") as f:
            f.write(f"🔧 DATABASE_URL: {db_url[:70]}...\n")
        
        result = add_user(
            user_id=user.id,
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
            web_app=WebAppInfo(url=f"{DOMAIN}/webapp")
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажми кнопку ниже:", reply_markup=reply_markup)
    
    with open("/tmp/webhook_debug.log", "a") as f:
        f.write(f"✅ START HANDLER COMPLETED\n\n")

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

# Инициализация базы данных при запуске
def initialize_database():
    try:
        # Устанавливаем DATABASE_URL если не установлен (для NetAngels)
        if not os.getenv("DATABASE_URL") and os.getenv("DB_CONNECTION_STRING"):
            os.environ["DATABASE_URL"] = os.getenv("DB_CONNECTION_STRING")
        
        print("🗄️ Инициализация базы данных...")
        print(f"📍 DATABASE_URL: {os.getenv('DATABASE_URL', 'НЕ НАЙДЕН')}")
        
        init_db()
        print("✅ База данных готова!")
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        # Не завершаем работу, так как таблицы могут уже существовать
        import traceback
        traceback.print_exc()
        return False

# Выполняем инициализацию
initialize_database()

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        
        # Записываем данные webhook в файл для отладки
        import json
        with open("/tmp/webhook_debug.log", "a") as f:
            f.write(f"=== {datetime.utcnow().isoformat()} ===\n")
            f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n\n")
        
        print("📩 Webhook получен:", data.get("message", {}).get("text", data))
        
        # Логируем информацию о пользователе
        if "message" in data and "from" in data["message"]:
            user = data["message"]["from"]
            print(f"👤 От пользователя: ID={user['id']}, username={user.get('username', 'None')}")
        
        update = Update.de_json(data, telegram_app.bot)
        print(f"🔄 Обрабатываем update: {update.update_id}")
        
        await telegram_app.process_update(update)
        print("✅ Update обработан успешно")
        
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ Ошибка в webhook: {e}")
        import traceback
        traceback.print_exc()
        
        # Записываем ошибку в файл
        with open("/tmp/webhook_debug.log", "a") as f:
            f.write(f"ERROR {datetime.utcnow().isoformat()}: {e}\n")
            f.write(traceback.format_exc() + "\n\n")
            
        return {"status": "error", "message": str(e)}

# === Тестовые маршруты ===
@app.get("/webhook-info")
async def webhook_info():
    """Информация о настройке webhook"""
    return {
        "webhook_url": WEBHOOK_URL,
        "webhook_path": WEBHOOK_PATH,
        "domain": DOMAIN,
        "token_set": bool(TOKEN)
    }

@app.get("/webhook-debug")
async def webhook_debug():
    """Просмотр логов webhook для отладки"""
    try:
        with open("/tmp/webhook_debug.log", "r") as f:
            logs = f.read()
        return {"logs": logs}
    except FileNotFoundError:
        return {"logs": "Лог-файл не найден"}

# === WebApp маршруты ===

app.mount("/webapp", StaticFiles(directory="static", html=True), name="webapp")
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")

# Главная страница - отдаем HTML файл
@app.get("/")
async def root():
    """Главная страница проекта"""
    return FileResponse("index.html")

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
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        items = get_shopping_items(db_user_id)
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
    shopping_list_id = data.get("shopping_list_id")
    url = data.get("url")
    comment = data.get("comment")

    if not name or not user_id:
        raise HTTPException(status_code=400, detail="name and user_id required")

    try:
        item_id = add_shopping_item(user_id, name, int(quantity), price, category, shopping_list_id, url, comment)
        return {"status": "ok", "id": item_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding shopping item: {str(e)}")

@app.put("/api/shopping/{item_id}")
async def update_shopping_item_endpoint(item_id: int, request: Request):
    """Обновить покупку"""
    data = await request.json()
    user_id = data.get("user_id")
    name = data.get("name")
    quantity = data.get("quantity", 1)
    price = data.get("price")
    category = data.get("category", "other")
    shopping_list_id = data.get("shopping_list_id")
    url = data.get("url")
    comment = data.get("comment")

    if not user_id or not name:
        raise HTTPException(status_code=400, detail="user_id and name required")

    try:
        success = update_shopping_item(item_id, user_id, name, int(quantity), price, category, shopping_list_id, url, comment)
        if not success:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating item: {str(e)}")

@app.post("/api/events")
async def create_event(request: Request):
    data = await request.json()
    title = data.get("title")
    location = data.get("location")
    start_at = data.get("start_at")
    end_at = data.get("end_at")
    user_id = data.get("user_id")
    project_id = data.get("project_id")
    description = data.get("description")

    if not all([title, user_id]):
        raise HTTPException(status_code=400, detail="Missing required fields: title and user_id")
    
    # Если location не указан, ставим значение по умолчанию
    if not location:
        location = "Не указано"

    # Если project_id None, получаем ID личного проекта пользователя
    if project_id is None:
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=400, detail="Пользователь не найден")
        project_id = get_user_personal_project_id(db_user_id)
        if not project_id:
            raise HTTPException(status_code=400, detail="Личный проект пользователя не найден")

    add_event(user_id, project_id, title, location, start_at, end_at, description)
    return {"status": "ok"}

@app.get("/api/events")
async def get_events(user_id: int, filter: str = "Предстоящие"):
    # Получаем ID пользователя из БД (основной ключ)
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    events = get_user_events(db_user_id, filter)
    return events

@app.get("/api/projects")
async def get_user_projects(user_id: int):
    """Получить проекты пользователя"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        from db import get_user_projects
        projects = get_user_projects(db_user_id)
        return projects
    except Exception as e:
        print(f"Ошибка получения проектов: {e}")
        return []

@app.get("/api/user-projects")
async def get_user_projects_alt(user_id: int):
    """Получить проекты пользователя (альтернативный endpoint)"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        from db import get_user_projects
        projects = get_user_projects(db_user_id)
        return projects
    except Exception as e:
        print(f"Ошибка получения проектов: {e}")
        return []

@app.post("/api/projects")
async def create_project(request: Request):
    """Создать новый проект"""
    try:
        data = await request.json()
        name = data.get("name")
        color = data.get("color", "#4facfe")
        owner_id = data.get("owner_id")
        
        if not name or not owner_id:
            raise HTTPException(status_code=400, detail="Name and owner_id are required")
        
        from db import create_project
        project = create_project(name, owner_id, color)
        return {"id": project, "name": name, "color": color, "owner_id": owner_id}
    except Exception as e:
        print(f"Ошибка создания проекта: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/projects/{project_id}")
async def update_project(project_id: int, request: Request):
    """Обновить проект"""
    try:
        data = await request.json()
        name = data.get("name")
        color = data.get("color", "#4facfe")
        owner_id = data.get("owner_id")
        
        if not name or not owner_id:
            raise HTTPException(status_code=400, detail="Name and owner_id are required")
        
        from db import update_project
        success = update_project(project_id, name, color, owner_id)
        
        if success:
            return {"id": project_id, "name": name, "color": color, "owner_id": owner_id}
        else:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка обновления проекта: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int, user_id: int):
    """Удалить проект"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        from db import delete_project
        success = delete_project(project_id, db_user_id)
        
        if success:
            return {"message": "Project deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка удаления проекта: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/projects/{project_id}/deactivate")
async def deactivate_project(project_id: int, request: Request):
    """Деактивировать проект"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        from db import deactivate_project
        success = deactivate_project(project_id, db_user_id)
        
        if success:
            return {"message": "Project deactivated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка деактивации проекта: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}")
async def get_project(project_id: int, user_id: int):
    """Получить информацию о проекте"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        from db import get_project
        project = get_project(project_id, db_user_id)
        
        if project:
            return project
        else:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка получения проекта: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}/members")
async def get_project_members(project_id: int, user_id: int):
    """Получить участников проекта"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        from db import get_project_members
        members = get_project_members(project_id, db_user_id)
        return members
    except Exception as e:
        print(f"Ошибка получения участников проекта: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/projects/{project_id}/members")
async def add_project_member(project_id: int, request: Request):
    """Добавить участника в проект"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        member_user_id = data.get("member_user_id")
        
        if not user_id or not member_user_id:
            raise HTTPException(status_code=400, detail="user_id and member_user_id are required")
        
        from db import add_project_member
        success = add_project_member(project_id, user_id, member_user_id)
        
        if success:
            return {"message": "Member added successfully"}
        else:
            raise HTTPException(status_code=404, detail="Project not found, access denied, or user not found")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка добавления участника: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/projects/{project_id}/members/{member_id}")
async def remove_project_member(project_id: int, member_id: int, request: Request):
    """Удалить участника из проекта"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        from db import remove_project_member
        success = remove_project_member(project_id, user_id, member_id)
        
        if success:
            return {"message": "Member removed successfully"}
        else:
            raise HTTPException(status_code=404, detail="Project not found, access denied, or member not found")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка удаления участника: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    # Получаем ID пользователя из БД (основной ключ)
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    settings = get_user_settings(db_user_id)
    if not isinstance(settings, dict):
        raise HTTPException(status_code=500, detail="Settings not loaded correctly")
    return {
        "timezone": settings.get("timezone", "0")
    }

@app.post("/api/user/settings")
async def set_user_settings(request: Request):
    data = await request.json()
    user_id = data.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")

    return {"status": "ok"}

# === User Timezone API ===
@app.get("/api/user/timezone")
async def get_user_timezone(user_id: int):
    """Получить часовой пояс пользователя"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        timezone = get_user_setting(db_user_id, "timezone") or "0"
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
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"🔍 Загрузка настроек для пользователя {user_id} (db_user_id: {db_user_id})")
        settings = get_user_settings(db_user_id)
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

# === Shopping Lists API ===

@app.get("/api/shopping-lists")
async def get_shopping_lists(user_id: int):
    """Получить все списки покупок пользователя"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        lists = get_user_shopping_lists(db_user_id)
        return lists
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching shopping lists: {str(e)}")

@app.post("/api/shopping-lists")
async def create_shopping_list_endpoint(request: Request):
    """Создать новый список покупок"""
    data = await request.json()
    name = data.get("name")
    project_id = data.get("project_id")
    user_id = data.get("user_id")

    if not all([name, project_id, user_id]):
        raise HTTPException(status_code=400, detail="name, project_id and user_id required")

    try:
        list_id = create_shopping_list(user_id, name, project_id)
        return {"status": "ok", "id": list_id}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating shopping list: {str(e)}")

@app.get("/api/shopping-lists/{list_id}")
async def get_shopping_list_endpoint(list_id: int, user_id: int):
    """Получить информацию о списке покупок"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        shopping_list = get_shopping_list(list_id, db_user_id)
        if not shopping_list:
            raise HTTPException(status_code=404, detail="Shopping list not found")
        return shopping_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching shopping list: {str(e)}")

@app.put("/api/shopping-lists/{list_id}")
async def update_shopping_list_endpoint(list_id: int, request: Request):
    """Обновить список покупок"""
    data = await request.json()
    name = data.get("name")
    project_id = data.get("project_id")
    user_id = data.get("user_id")

    if not all([name, project_id, user_id]):
        raise HTTPException(status_code=400, detail="name, project_id and user_id required")

    try:
        success = update_shopping_list(list_id, user_id, name, project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Shopping list not found")
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating shopping list: {str(e)}")

@app.delete("/api/shopping-lists/{list_id}")
async def delete_shopping_list_endpoint(list_id: int, user_id: int):
    """Удалить список покупок"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = delete_shopping_list(list_id, db_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Shopping list not found")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting shopping list: {str(e)}")

@app.get("/api/shopping-by-lists")
async def get_shopping_by_lists(user_id: int):
    """Получить покупки, сгруппированные по спискам"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        items = get_shopping_items_by_lists(db_user_id)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching shopping items by lists: {str(e)}")

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
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        stats = get_user_stats(db_user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user stats: {str(e)}")

@app.get("/api/dashboard-counters")
async def get_dashboard_counters_endpoint(user_id: int):
    """Получить счетчики для навигации dashboard"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        counters = get_dashboard_counters(db_user_id)
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
        
        # Проверяем время авторизации (не старше 1 часа)
        auth_date = data.get("auth_date")
        if auth_date:
            import time
            current_time = int(time.time())
            auth_time = int(auth_date)
            time_diff = current_time - auth_time
            
            print(f"🕐 Время авторизации: {auth_time}, текущее: {current_time}, разница: {time_diff}с")
            
            # Если авторизация старше 1 часа (3600 секунд), отклоняем
            if time_diff > 3600:
                print("❌ Авторизация устарела")
                raise HTTPException(status_code=401, detail="Authorization expired")
        
        # Добавляем пользователя в базу данных
        print("💾 Добавляем пользователя в БД...")
        user_id_from_db = add_user(user_id, first_name, username)
        
        if not user_id_from_db:
            print("❌ Не удалось создать пользователя в БД")
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        print(f"✅ Пользователь создан с ID: {user_id_from_db}")
        
        # Проверяем, что личный проект создан
        personal_project_id = get_user_personal_project_id(user_id_from_db)
        if not personal_project_id:
            print("❌ Личный проект не найден после создания пользователя")
            raise HTTPException(status_code=500, detail="Failed to create personal project")
        
        print(f"✅ Личный проект найден: {personal_project_id}")
        
        result = {
            "status": "ok", 
            "user": {
                "id": user_id_from_db,  # Правильный ID из БД
                "telegram_id": user_id,  # ID телеграм аккаунта  
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "photo_url": photo_url,
                "personal_project_id": personal_project_id
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

@app.get("/api/user/validate")
async def validate_user(user_id: int):
    """
    Проверяет, что пользователь существует в БД и имеет личный проект
    """
    try:
        print(f"🔍 Валидация пользователя {user_id}")
        
        # Проверяем, что пользователь существует
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            print(f"❌ Пользователь {user_id} не найден в БД")
            return {"valid": False, "reason": "User not found"}
        
        # Проверяем, что у пользователя есть личный проект
        personal_project_id = get_user_personal_project_id(db_user_id)
        if not personal_project_id:
            print(f"❌ У пользователя {user_id} (db_user_id: {db_user_id}) нет личного проекта")
            return {"valid": False, "reason": "Personal project not found"}
        
        print(f"✅ Пользователь {user_id} валиден (db_user_id: {db_user_id}, personal_project: {personal_project_id})")
        return {
            "valid": True, 
            "id": db_user_id,  # Правильный ID из БД
            "telegram_id": user_id,  # ID телеграм аккаунта
            "personal_project_id": personal_project_id
        }
        
    except Exception as e:
        print(f"❌ Ошибка валидации пользователя {user_id}: {e}")
        return {"valid": False, "reason": f"Server error: {str(e)}"}

# === Task API ===
from db import add_task, get_tasks, complete_task, get_user_personal_project_id
from typing import Optional

@app.get("/api/tasks")
async def api_get_tasks(user_id: int, project_id: Optional[int] = None):
    """Получить задачи пользователя с учетом часового пояса"""
    from datetime_utils import format_datetime_for_user, is_today, is_tomorrow, is_overdue
    
    # Получаем ID пользователя из БД (основной ключ)
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем задачи из БД
    tasks = get_tasks(db_user_id, project_id)
    
    # Получаем часовой пояс пользователя
    user_timezone = get_user_setting(db_user_id, "timezone") or "0"
    
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

@app.get("/api/tasks/today")
async def api_today_tasks(user_id: int):
    # Получаем ID пользователя из БД (основной ключ)
    db_user_id = resolve_user_id(user_id)
    if not db_user_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = get_today_tasks(user_id)
    return {
        "overdue": result.get("overdue", []),
        "today": result.get("today", [])
    }

@app.get("/api/tasks/{task_id}")
async def api_get_task(task_id: int, user_id: int):
    """Получить одну задачу по ID"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
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
                """, (task_id, db_user_id, db_user_id, db_user_id))
                
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

    # Если project_id None, получаем ID личного проекта пользователя
    if project_id is None:
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=400, detail="Пользователь не найден")
        project_id = get_user_personal_project_id(db_user_id)
        if not project_id:
            raise HTTPException(status_code=400, detail="Личный проект пользователя не найден")
    
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

@app.post("/api/debug/add-user-to-project")
async def debug_add_user_to_project(request: Request):
    """Отладочный эндпоинт для добавления пользователя в проект"""
    data = await request.json()
    user_id = data.get("user_id")
    project_id = data.get("project_id")
    
    if not user_id or not project_id:
        raise HTTPException(status_code=400, detail="user_id and project_id required")
    
    try:
        add_project_member(project_id, user_id)
        return {"status": "ok", "message": f"User {user_id} added to project {project_id}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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

# === Notes API ===
from db import add_note, get_user_notes, get_note_by_id, update_note, delete_note

@app.get("/api/notes")
async def api_get_notes(user_id: int):
    """Получить все заметки пользователя"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        notes = get_user_notes(db_user_id)
        return notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notes: {str(e)}")

@app.get("/api/notes/{note_id}")
async def api_get_note(note_id: int, user_id: int):
    """Получить заметку по ID"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        note = get_note_by_id(note_id, db_user_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching note: {str(e)}")

@app.post("/api/notes")
async def api_create_note(request: Request):
    """Создать новую заметку"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        title = data.get("title")
        content = data.get("content", "")
        
        if not user_id or not title:
            raise HTTPException(status_code=400, detail="user_id and title are required")
        
        # Получаем ID пользователя из БД (основной ключ) (функция add_note уже делает это, но для консистентности)
        note_id = add_note(user_id, title, content)
        return {"status": "ok", "id": note_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating note: {str(e)}")

@app.put("/api/notes/{note_id}")
async def api_update_note(note_id: int, request: Request):
    """Обновить заметку"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        title = data.get("title")
        content = data.get("content", "")
        
        if not user_id or not title:
            raise HTTPException(status_code=400, detail="user_id and title are required")
        
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = update_note(note_id, db_user_id, title, content)
        if not success:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating note: {str(e)}")

@app.delete("/api/notes/{note_id}")
async def api_delete_note(note_id: int, user_id: int):
    """Удалить заметку"""
    try:
        # Получаем ID пользователя из БД (основной ключ)
        db_user_id = resolve_user_id(user_id)
        if not db_user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = delete_note(note_id, db_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting note: {str(e)}")

# === Startup ===
@app.on_event("startup")
async def on_startup():
    # Инициализация БД перенесена в start_server.py
    try:
        await telegram_app.initialize()
        await telegram_app.bot.delete_webhook()
        
        # Устанавливаем webhook для получения обновлений
        await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
        print(f"✅ Webhook установлен: {WEBHOOK_URL}")
        
        await telegram_app.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="Открыть WebApp",
                web_app=WebAppInfo(url=f"{DOMAIN}/webapp")
            )
        )
        asyncio.create_task(reminder_loop())
        
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