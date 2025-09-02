"""
API для дней рождения
"""
from typing import Optional, List
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Request

from app.database.repositories.birthday_repository import birthday_repository

router = APIRouter()


def _compute_days_until(day: int, month: int) -> int:
    today = date.today()
    year = today.year
    try:
        next_bd = date(year, month, day)
    except ValueError:
        # На случай невалидных комбинаций (29 февр. в невисокосный год) — переносим на 28 февр.
        if month == 2 and day == 29:
            next_bd = date(year, 2, 28)
        else:
            raise
    if next_bd < today:
        # следующий год
        try:
            next_bd = date(year + 1, month, day)
        except ValueError:
            if month == 2 and day == 29:
                next_bd = date(year + 1, 2, 28)
            else:
                raise
    return (next_bd - today).days


@router.get("/birthdays")
async def list_birthdays(user_id: int, page: int = 1, limit: int = 20):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid pagination params")
    try:
        items = birthday_repository.get_birthdays(user_id, limit, (page - 1) * limit)

        # Сортируем по ближайшей дате (дней до даты)
        def sort_key(it):
            return _compute_days_until(int(it["day"]), int(it["month"]))

        items_sorted = sorted(items, key=sort_key)
        total = birthday_repository.count_birthdays(user_id)

        # Пагинация в памяти (так как сортировка по вычисляемому ключу)
        start = (page - 1) * limit
        end = start + limit
        page_items = items_sorted[start:end]

        # Добавляем производные поля
        enriched = []
        for it in page_items:
            days_until = _compute_days_until(int(it["day"]), int(it["month"]))
            enriched.append({
                **it,
                "days_until": days_until,
            })

        return {
            "items": enriched,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching birthdays: {e}")


@router.post("/birthdays")
async def create_birthday(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    full_name = data.get("full_name")
    day = data.get("day")
    month = data.get("month")
    year = data.get("year")
    description = data.get("description")

    if not user_id or not full_name or not day or not month:
        raise HTTPException(status_code=400, detail="user_id, full_name, day, month required")
    try:
        bid = birthday_repository.create_birthday(user_id, full_name, int(day), int(month), int(year) if year else None, description)
        if not bid:
            raise HTTPException(status_code=500, detail="Failed to create birthday")
        return {"status": "ok", "id": bid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating birthday: {e}")


@router.get("/birthdays/{birthday_id}")
async def get_birthday(birthday_id: int, user_id: int):
    try:
        item = birthday_repository.get_birthday(user_id, birthday_id)
        if not item:
            raise HTTPException(status_code=404, detail="Birthday not found")
        item["days_until"] = _compute_days_until(int(item["day"]), int(item["month"]))
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching birthday: {e}")


@router.put("/birthdays/{birthday_id}")
async def update_birthday(birthday_id: int, request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    full_name = data.get("full_name")
    day = data.get("day")
    month = data.get("month")
    year = data.get("year")
    description = data.get("description")

    if not user_id or not full_name or not day or not month:
        raise HTTPException(status_code=400, detail="user_id, full_name, day, month required")
    try:
        ok = birthday_repository.update_birthday(user_id, birthday_id, full_name, int(day), int(month), int(year) if year else None, description)
        if not ok:
            raise HTTPException(status_code=404, detail="Birthday not found")
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating birthday: {e}")


@router.delete("/birthdays/{birthday_id}")
async def delete_birthday(birthday_id: int, request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    try:
        ok = birthday_repository.delete_birthday(user_id, birthday_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Birthday not found")
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting birthday: {e}")

