"""
API для работы с тегами
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database.repositories.tag_repository import TagRepository, TagAssociationRepository
from app.database.models.tag import Tag, TagAssociation

router = APIRouter()


class TagCreateRequest(BaseModel):
    """Модель для создания тега"""
    name: str
    background_color: str = "#6366f1"
    project_id: int


class TagUpdateRequest(BaseModel):
    """Модель для обновления тега"""
    name: str
    background_color: str


class TagResponse(BaseModel):
    """Модель для ответа тега"""
    id: int
    name: str
    background_color: str
    project_id: int
    created_by_id: int
    created_at: str
    active: bool


class TagAssociationRequest(BaseModel):
    """Модель для добавления тега к объекту"""
    tag_id: int
    object_type: str  # 'task', 'event', 'purchase'
    object_id: int


@router.get("/tags/{project_id}")
async def get_project_tags(project_id: int, active_only: bool = True):
    """Получить все теги проекта"""
    try:
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")
        
        tags = TagRepository.get_project_tags(project_id, active_only)
        
        return {
            "tags": [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "background_color": tag.background_color,
                    "project_id": tag.project_id,
                    "created_by_id": tag.created_by_id,
                    "created_at": tag.created_at,
                    "active": tag.active
                }
                for tag in tags
            ],
            "count": len(tags)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tags: {str(e)}")


@router.post("/tags")
async def create_tag(request: TagCreateRequest, user_id: int = Query(...)):
    """Создать новый тег"""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    try:
        if not request.name or not request.name.strip():
            raise HTTPException(status_code=400, detail="Tag name is required")
        
        if len(request.name) > 50:
            raise HTTPException(status_code=400, detail="Tag name is too long (max 50 characters)")
        
        if not TagRepository.check_tag_exists(request.project_id, request.name.strip()):
            tag = Tag(
                name=request.name.strip(),
                background_color=request.background_color,
                project_id=request.project_id,
                created_by_id=user_id,
                created_at=datetime.now().isoformat(),
                active=True
            )
            
            created_tag = TagRepository.create_tag(tag)
            if created_tag:
                return {
                    "id": created_tag.id,
                    "name": created_tag.name,
                    "background_color": created_tag.background_color,
                    "project_id": created_tag.project_id,
                    "created_by_id": created_tag.created_by_id,
                    "created_at": created_tag.created_at,
                    "active": created_tag.active
                }
        else:
            raise HTTPException(status_code=409, detail="Tag with this name already exists in the project")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating tag: {str(e)}")


@router.get("/tag/{tag_id}")
async def get_tag(tag_id: int):
    """Получить информацию о теге"""
    try:
        if not tag_id:
            raise HTTPException(status_code=400, detail="tag_id is required")
        
        tag = TagRepository.get_tag(tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        return {
            "id": tag.id,
            "name": tag.name,
            "background_color": tag.background_color,
            "project_id": tag.project_id,
            "created_by_id": tag.created_by_id,
            "created_at": tag.created_at,
            "active": tag.active
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tag: {str(e)}")


@router.put("/tag/{tag_id}")
async def update_tag(tag_id: int, request: TagUpdateRequest):
    """Обновить тег"""
    try:
        if not tag_id:
            raise HTTPException(status_code=400, detail="tag_id is required")
        
        if not request.name or not request.name.strip():
            raise HTTPException(status_code=400, detail="Tag name is required")
        
        current_tag = TagRepository.get_tag(tag_id)
        if not current_tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        if TagRepository.check_tag_exists(current_tag.project_id, request.name.strip(), exclude_id=tag_id):
            raise HTTPException(status_code=409, detail="Tag with this name already exists in the project")
        
        updated_tag = Tag(
            id=tag_id,
            name=request.name.strip(),
            background_color=request.background_color,
            project_id=current_tag.project_id,
            created_by_id=current_tag.created_by_id,
            created_at=current_tag.created_at,
            active=current_tag.active
        )
        
        success = TagRepository.update_tag(updated_tag)
        if success:
            return {
                "id": updated_tag.id,
                "name": updated_tag.name,
                "background_color": updated_tag.background_color,
                "project_id": updated_tag.project_id,
                "created_by_id": updated_tag.created_by_id,
                "created_at": updated_tag.created_at,
                "active": updated_tag.active
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update tag")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating tag: {str(e)}")


@router.delete("/tag/{tag_id}")
async def delete_tag(tag_id: int):
    """Удалить тег"""
    try:
        if not tag_id:
            raise HTTPException(status_code=400, detail="tag_id is required")
        
        tag = TagRepository.get_tag(tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        success = TagRepository.delete_tag(tag_id)
        if success:
            return {"message": "Tag deleted successfully", "tag_id": tag_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete tag")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting tag: {str(e)}")


@router.post("/tag/assign")
async def assign_tag_to_object(request: TagAssociationRequest):
    """Добавить тег к объекту (задача, встреча, покупка)"""
    try:
        if not request.tag_id or not request.object_type or not request.object_id:
            raise HTTPException(status_code=400, detail="tag_id, object_type, and object_id are required")
        
        if request.object_type not in ['task', 'event', 'purchase']:
            raise HTTPException(status_code=400, detail="object_type must be 'task', 'event', or 'purchase'")
        
        tag = TagRepository.get_tag(request.tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        association = TagAssociationRepository.add_tag_to_object(
            request.tag_id,
            request.object_type,
            request.object_id
        )
        
        if association:
            return {
                "id": association.id,
                "tag_id": association.tag_id,
                "object_type": association.object_type,
                "object_id": association.object_id,
                "created_at": association.created_at
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to assign tag to object")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assigning tag: {str(e)}")


@router.delete("/tag/unassign/{tag_id}/{object_type}/{object_id}")
async def unassign_tag_from_object(tag_id: int, object_type: str, object_id: int):
    """Удалить тег от объекта"""
    try:
        if not tag_id or not object_type or not object_id:
            raise HTTPException(status_code=400, detail="tag_id, object_type, and object_id are required")
        
        if object_type not in ['task', 'event', 'purchase']:
            raise HTTPException(status_code=400, detail="object_type must be 'task', 'event', or 'purchase'")
        
        success = TagAssociationRepository.remove_tag_from_object(tag_id, object_type, object_id)
        if success:
            return {"message": "Tag removed from object successfully"}
        else:
            raise HTTPException(status_code=404, detail="Tag association not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing tag: {str(e)}")


@router.get("/object/tags/{object_type}/{object_id}")
async def get_object_tags(object_type: str, object_id: int):
    """Получить все теги объекта"""
    try:
        if not object_type or not object_id:
            raise HTTPException(status_code=400, detail="object_type and object_id are required")
        
        if object_type not in ['task', 'event', 'purchase']:
            raise HTTPException(status_code=400, detail="object_type must be 'task', 'event', or 'purchase'")
        
        tags = TagAssociationRepository.get_object_tags(object_type, object_id)
        
        return {
            "tags": [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "background_color": tag.background_color,
                    "project_id": tag.project_id,
                    "created_by_id": tag.created_by_id,
                    "created_at": tag.created_at,
                    "active": tag.active
                }
                for tag in tags
            ],
            "count": len(tags)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching object tags: {str(e)}")


@router.get("/tag/{tag_id}/objects/{object_type}")
async def get_objects_by_tag(tag_id: int, object_type: str):
    """Получить все объекты с данным тегом"""
    try:
        if not tag_id or not object_type:
            raise HTTPException(status_code=400, detail="tag_id and object_type are required")
        
        if object_type not in ['task', 'event', 'purchase']:
            raise HTTPException(status_code=400, detail="object_type must be 'task', 'event', or 'purchase'")
        
        tag = TagRepository.get_tag(tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        associations = TagAssociationRepository.get_objects_by_tag(tag_id)
        filtered_associations = [a for a in associations if a.object_type == object_type]
        
        return {
            "associations": [
                {
                    "id": assoc.id,
                    "tag_id": assoc.tag_id,
                    "object_type": assoc.object_type,
                    "object_id": assoc.object_id,
                    "created_at": assoc.created_at
                }
                for assoc in filtered_associations
            ],
            "count": len(filtered_associations)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching objects by tag: {str(e)}")
