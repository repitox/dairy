"""
API для работы с покупками
"""
from fastapi import APIRouter, Request, HTTPException
from app.database.repositories.shopping_repository import shopping_repository

router = APIRouter()


@router.get("/shopping")
async def get_shopping(user_id: int):
    """Получить список покупок пользователя"""
    try:
        items = shopping_repository.get_shopping_items(user_id)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching shopping items: {str(e)}")


@router.post("/shopping")
async def add_to_shopping(request: Request):
    """Добавить новую покупку"""
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
        item_id = shopping_repository.add_shopping_item(
            user_id, name, int(quantity), price, category, shopping_list_id, url, comment
        )
        return {"status": "ok", "id": item_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding shopping item: {str(e)}")


@router.put("/shopping/{item_id}")
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
        success = shopping_repository.update_shopping_item(
            item_id, user_id, name, int(quantity), price, category, shopping_list_id, url, comment
        )
        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail="Shopping item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating shopping item: {str(e)}")


@router.post("/shopping/{item_id}/toggle")
async def toggle_shopping_item_endpoint(item_id: int, request: Request):
    """Переключить статус покупки"""
    data = await request.json()
    user_id = data.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    try:
        success = shopping_repository.toggle_shopping_item(item_id, user_id)
        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail="Shopping item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling shopping item: {str(e)}")


@router.delete("/shopping/{item_id}")
async def delete_shopping_item_endpoint(item_id: int, request: Request):
    """Удалить покупку"""
    data = await request.json()
    user_id = data.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    try:
        success = shopping_repository.delete_shopping_item(item_id, user_id)
        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail="Shopping item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting shopping item: {str(e)}")


@router.get("/shopping-lists")
async def get_shopping_lists(user_id: int):
    """Получить списки покупок пользователя"""
    try:
        lists = shopping_repository.get_user_shopping_lists(user_id)
        return lists
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching shopping lists: {str(e)}")


@router.post("/shopping-lists")
async def create_shopping_list_endpoint(request: Request):
    """Создать новый список покупок"""
    data = await request.json()
    name = data.get("name")
    user_id = data.get("user_id")
    project_id = data.get("project_id")

    if not name or not user_id:
        raise HTTPException(status_code=400, detail="name and user_id required")

    try:
        list_id = shopping_repository.create_shopping_list(name, user_id, project_id)
        return {"status": "ok", "id": list_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating shopping list: {str(e)}")