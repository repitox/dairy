import json
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Optional
import pytz
import requests
from db import get_today_tasks, get_today_events, get_recent_purchases, get_conn
import os
from datetime import datetime
from pytz import timezone

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Глобальные объекты/флаги для предотвращения дублей
_scheduler: Optional[BackgroundScheduler] = None
_scheduler_started: bool = False

def send_daily_summary():
    print("⏰ Запуск ежедневной рассылки...")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT telegram_id FROM users WHERE telegram_id IS NOT NULL")
            users = cur.fetchall()
            print("💬 Все telegram_id из БД:", users)
            print(f"🔍 Найдено пользователей: {len(users)}")

    for row in users:
        user_telegram_id = row["telegram_id"]
        print(f"📤 Отправка сводки для пользователя {user_telegram_id}...")

        try:
            # Получаем задачи пользователя (включая просроченные и на сегодня)
            tasks_data = get_today_tasks(user_telegram_id)
            print(f"🔍 Данные задач для {user_telegram_id}: {tasks_data}")
            
            # Объединяем просроченные и сегодняшние задачи
            all_tasks = []
            if isinstance(tasks_data, dict):
                overdue_tasks = tasks_data.get('overdue', [])
                today_tasks = tasks_data.get('today', [])
                all_tasks = overdue_tasks + today_tasks
            else:
                # Если вернулся старый формат
                all_tasks = tasks_data if isinstance(tasks_data, list) else []
            
            # Получаем события пользователя
            events = get_today_events(user_telegram_id)
            print(f"🔍 События для {user_telegram_id}: {events}")
            
            # Получаем покупки пользователя
            shopping = get_recent_purchases(user_telegram_id)
            print(f"🔍 Покупки для {user_telegram_id}: {shopping}")

            # Форматируем и отправляем сообщение (с полным планом на день)
            message = format_summary_v2(all_tasks, events, shopping, user_telegram_id)
            send_message(user_telegram_id, message)
            
        except Exception as e:
            print(f"❌ Ошибка при обработке пользователя {user_telegram_id}: {e}")
            continue

def format_summary_v2(tasks, events, shopping, user_id):
    """
    Новая версия форматирования сводки для конкретного пользователя
    """
    from datetime import datetime
    from pytz import timezone
    
    lines = []
    tz = timezone("Europe/Moscow")
    now = datetime.now(tz)
    
    print(f"🔍 Форматирование для пользователя {user_id}")
    print(f"📋 Задач получено: {len(tasks) if tasks else 0}")
    print(f"📅 События получено: {len(events) if events else 0}")
    print(f"🛒 Покупок получено: {len(shopping) if shopping else 0}")
    
    # Заголовок сводки
    lines.append(f"🌅 <b>Доброе утро!</b>")
    lines.append(f"📅 Сегодня {now.strftime('%d.%m.%Y')}")
    lines.append("")
    
    # Обрабатываем задачи
    if tasks:
        # Разделяем на просроченные и сегодняшние
        overdue = []
        today = []
        
        for task in tasks:
            if not task:
                continue
                
            # Преобразуем в словарь если нужно
            if hasattr(task, 'keys'):
                task_dict = dict(task)
            else:
                task_dict = task
            
            # Проверяем завершенность
            is_completed = task_dict.get('completed', False) or task_dict.get('is_done', False)
            if is_completed:
                continue
                
            due_date_str = task_dict.get('due_date')
            if not due_date_str:
                continue
                
            try:
                # Парсим дату
                if 'T' in due_date_str:
                    if due_date_str.endswith('Z'):
                        due_dt = datetime.fromisoformat(due_date_str[:-1]).replace(tzinfo=tz)
                    else:
                        due_dt = datetime.fromisoformat(due_date_str).astimezone(tz)
                else:
                    due_dt = datetime.strptime(due_date_str, '%Y-%m-%d').replace(tzinfo=tz)
                
                if due_dt.date() < now.date():
                    overdue.append(task_dict)
                elif due_dt.date() == now.date():
                    today.append(task_dict)
                    
            except (ValueError, TypeError) as e:
                print(f"⚠️ Ошибка парсинга даты {due_date_str}: {e}")
                continue
        
        # Выводим просроченные задачи
        if overdue:
            lines.append("⏰ <b>Просроченные задачи</b>:")
            for task in sorted(overdue, key=lambda x: x.get('priority') == 'важная', reverse=True):
                title = task.get('title', 'Без названия')
                priority_icon = "❗️" if task.get('priority') == 'важная' else "▪️"
                project_name = task.get('project_name', '')
                project_info = f" ({project_name})" if project_name else " (Личное)"
                lines.append(f"{priority_icon} {title}{project_info}")
            lines.append("")
        
        # Выводим задачи на сегодня
        if today:
            lines.append("📌 <b>Задачи на сегодня</b>:")
            for task in sorted(today, key=lambda x: x.get('priority') == 'важная', reverse=True):
                title = task.get('title', 'Без названия')
                priority_icon = "❗️" if task.get('priority') == 'важная' else "▪️"
                project_name = task.get('project_name', '')
                project_info = f" ({project_name})" if project_name else " (Личное)"
                
                # Добавляем время если есть
                due_date_str = task.get('due_date', '')
                time_info = ""
                if len(due_date_str) > 10 and 'T' in due_date_str:
                    try:
                        time_part = due_date_str.split('T')[1][:5]  # HH:MM
                        time_info = f" в {time_part}"
                    except:
                        pass
                
                lines.append(f"{priority_icon} {title}{time_info}{project_info}")
            lines.append("")
        
        if not overdue and not today:
            lines.append("📌 <b>Задачи</b>: Задач нет! 🎉")
            lines.append("")
    else:
        lines.append("📌 <b>Задачи</b>: Задач нет! 🎉")
        lines.append("")
    
    # Обрабатываем события
    if events:
        lines.append("📅 <b>Встречи на сегодня</b>:")
        for event in events:
            if not event:
                continue
                
            # Преобразуем в словарь если нужно
            if hasattr(event, 'keys'):
                event_dict = dict(event)
            else:
                event_dict = event
            
            title = event_dict.get('title', 'Без названия')
            location = event_dict.get('location', '')
            project_name = event_dict.get('project_name', '')
            
            # Форматируем время
            start_at_str = event_dict.get('start_at', '')
            time_info = ""
            if start_at_str:
                try:
                    if 'T' in start_at_str:
                        time_part = start_at_str.split('T')[1][:5]  # HH:MM
                        time_info = f" в {time_part}"
                except:
                    pass
            
            # Собираем строку
            location_info = f", {location}" if location else ""
            project_info = f" ({project_name})" if project_name else " (Личное)"
            
            lines.append(f"🕘 {title}{time_info}{location_info}{project_info}")
        lines.append("")
    else:
        lines.append("📅 <b>Встречи</b>: Сегодня встреч нет")
        lines.append("")
    
    # Обрабатываем покупки
    if shopping:
        lines.append("🛒 <b>Нужно купить</b>:")
        for item in shopping:
            if not item:
                continue
                
            # Преобразуем в словарь если нужно
            if hasattr(item, 'keys'):
                item_dict = dict(item)
            else:
                item_dict = item
            
            title = item_dict.get('item', item_dict.get('title', 'Без названия'))
            quantity = item_dict.get('quantity', '')
            
            quantity_info = f"{quantity} × " if quantity else ""
            lines.append(f"▪️ {quantity_info}{title}")
        lines.append("")
    else:
        lines.append("🛒 <b>Покупки</b>: Всё куплено! ✅")
        lines.append("")
    
    # Добавляем мотивирующее сообщение
    lines.append("💪 Удачного дня!")
    
    result = "\n".join(lines)
    print(f"📨 Итоговое сообщение для {user_id}:")
    print(result)
    print("=" * 50)
    
    return result



def send_message(user_id, text):
    print(f"📨 Отправка сообщения Telegram для {user_id}")
    try:
        response = requests.post(API_URL, data={"chat_id": user_id, "text": text, "parse_mode": "HTML"})
        print(f"➡️ Статус ответа: {response.status_code}")
        if response.status_code == 200:
            print("✅ Сообщение отправлено успешно")
        else:
            print(f"❌ Ошибка отправки: {response.text}")
    except Exception as e:
        print(f"❌ Исключение при отправке: {e}")

def test_daily_summary():
    """
    Функция для тестирования рассылки - отправляет сводку прямо сейчас
    """
    print("🧪 ТЕСТОВАЯ рассылка...")
    send_daily_summary()

# Запуск планировщика
def start_scheduler():
    """Идempotent запуск планировщика.

    - Не даёт создать несколько инстансов/задач при повторном вызове
    - Задаче присваивается стабильный id, чтобы исключить дублирование
    """
    global _scheduler, _scheduler_started

    if _scheduler_started and _scheduler is not None:
        print("ℹ️ Планировщик уже запущен — пропускаем повторный старт.")
        return

    print("🌀 Планировщик запускается...")
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone=pytz.timezone("Europe/Moscow"))

    # Добавляем id для задачи и разрешаем замену, чтобы избежать дублей
    _scheduler.add_job(
        send_daily_summary,
        "cron",
        hour=9,
        minute=1,
        id="daily_summary",
        replace_existing=True,
    )
    _scheduler.start()
    _scheduler_started = True
    print("✅ Планировщик запущен.")
