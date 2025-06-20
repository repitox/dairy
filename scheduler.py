import json
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import requests
from db import get_today_tasks, get_today_events, get_recent_purchases, get_conn
import os
from datetime import datetime
from pytz import timezone

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_daily_summary():
    print("⏰ Запуск ежедневной рассылки...")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users")
            users = cur.fetchall()
            print("💬 Все user_id из БД:", users)
            print(f"🔍 Найдено пользователей: {len(users)}")

    for row in users:
        user_id = row["user_id"]
        print(f"📤 Отправка сводки для пользователя {user_id}...")

        tasks_by_group = get_today_tasks(user_id)
        tasks_raw = []
        for group in tasks_by_group.values():
            tasks_raw.extend(group)
        def safe_parse(data):
            if isinstance(data, dict):
                return data
            if hasattr(data, 'keys'):  # например, RealDictRow
                return dict(data)
            try:
                return json.loads(data) if isinstance(data, str) and data else data
            except json.JSONDecodeError:
                print(f"⚠️ Ошибка парсинга JSON: {data}")
                return None
        tasks = [safe_parse(t) for t in tasks_raw if safe_parse(t)]

        events_raw = get_today_events(user_id)
        events = [safe_parse(e) for e in events_raw if safe_parse(e)]

        shopping_raw = get_recent_purchases(user_id)
        shopping = [safe_parse(s) for s in shopping_raw if safe_parse(s)]

        message = format_summary(tasks, events, shopping)
        send_message(user_id, message)

# def format_summary(tasks, events, shopping):
#     lines = ["📌 <b>Задачи</b>:"]
#     lines += [f"- [ ] {t.get('title', 'Без названия')} ({t.get('due_date', 'нет даты')})" for t in tasks] or ["Нет задач"]

#     lines += ["", "📅 <b>Встречи</b>:"]
#     lines += [f"- {e.get('title', 'Без названия')} — {e.get('start_at', '')[11:16]}" for e in events] or ["Нет встреч"]

#     lines += ["", "🛒 <b>Покупки</b>:"]
#     lines += [f"- {s.get('title', 'Без названия')}" for s in shopping] or ["Нет покупок"]

#     return "\n".join(lines)

def format_summary(tasks, events, shopping):
    lines = []

    tz = timezone("Europe/Moscow")
    now = datetime.now(tz)
    today_str = now.strftime("%Y-%m-%d")

    overdue = [t for t in tasks if not t.get("is_done") and t.get("overdue")]
    today = [t for t in tasks if not t.get("is_done") and (t.get("due_date") or "").startswith(today_str)]

    today_ids = {t.get("id") for t in today}
    filtered_overdue = [t for t in overdue if t.get("id") not in today_ids]

    if filtered_overdue:
        lines.append("\n⏰ <b>Просроченные задачи</b>:")
        for t in filtered_overdue:
            title = t.get("title", "Без названия")
            time = t.get("due_date", "")
            prio = "‼️" if t.get("priority") == "важная" else "•"
            project = f"({t.get('project_title')})" if t.get("project_title") else ""
            time_str = time[11:16] if len(time) >= 16 else "без срока"
            lines.append(f"{prio} [ ] {title} — {time_str} {project}")

    if today:
        lines.append("\n📌 <b>Задачи на сегодня</b>:")
        for t in today:
            title = t.get("title", "Без названия")
            time = t.get("due_date", "")
            prio = "‼️" if t.get("priority") == "важная" else "•"
            project = f"({t.get('project_title')})" if t.get("project_title") else ""
            suffix = f"{time[11:16]}" if len(time) >= 16 else "без срока"
            lines.append(f"{prio} [ ] {title} — {suffix} {project}")
    if not filtered_overdue and not today:
        lines.append("📌 <b>Задачи</b>: Задач нет 🎉")

    # === СОБЫТИЯ ===
    if events:
        lines.append("\n📅 <b>Встречи</b>:")
        for e in events:
            title = e.get("title", "Без названия")
            time = e.get("start_at", "")
            loc = e.get("location", "")
            project = f"({e.get('project_title')})" if e.get("project_title") else ""
            time_str = time[11:16] if len(time) >= 16 else "время не указано"
            lines.append(f"🕘 {title} — {time_str} {loc} {project}")
    else:
        lines.append("\n📅 <b>Встречи</b>: Сегодня встреч нет")

    # === ПОКУПКИ ===
    if shopping:
        lines.append("\n🛒 <b>Покупки</b>:")
        for s in shopping:
            title = s.get("title", "Без названия")
            count = s.get("quantity")
            done = s.get("is_done", False)
            check = "✅" if done else "❌"
            prefix = f"{count} × " if count else ""
            lines.append(f"{check} {prefix}{title}")
    else:
        lines.append("\n🛒 <b>Покупки</b>: Всё куплено!")

    return "\n".join(lines)

def send_message(user_id, text):
    print(f"📨 Отправка сообщения Telegram для {user_id}")
    response = requests.post(API_URL, data={"chat_id": user_id, "text": text, "parse_mode": "HTML"})
    print(f"➡️ Статус ответа: {response.status_code}, текст: {response.text}")

# Запуск планировщика
def start_scheduler():
    print("🌀 Планировщик запускается...")
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Europe/Moscow"))
    scheduler.add_job(send_daily_summary, "cron", hour=11, minute=31)
    scheduler.start()
    print("✅ Планировщик запущен.")