"""
API для работы с проектами
"""
from fastapi import APIRouter, HTTPException
from app.database.repositories.user_repository import user_repository
from app.database.connection import get_db_cursor
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()


class CreateProjectRequest(BaseModel):
    """Модель для создания проекта"""
    name: str
    color: Optional[str] = None
    description: Optional[str] = None
    owner_id: int


class InviteRequest(BaseModel):
    """Модель для запроса приглашения участника"""
    project_id: int
    user_id: int


class UpdateProjectRequest(BaseModel):
    """Модель для обновления проекта"""
    name: str
    color: Optional[str] = None
    description: Optional[str] = None


class RemoveMemberRequest(BaseModel):
    """Модель для удаления участника"""
    project_id: int
    user_id: int


@router.post("/projects")
async def create_project(request: CreateProjectRequest):
    """Создать новый проект"""
    try:
        if not request.name:
            raise HTTPException(status_code=400, detail="name is required")
        
        if not request.owner_id:
            raise HTTPException(status_code=400, detail="owner_id is required")
        
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO projects (name, owner_id, color, description, created_at, active)
                VALUES (%s, %s, %s, %s, %s, true)
                RETURNING id, name, owner_id, color, description, created_at, active
            """, (
                request.name,
                request.owner_id,
                request.color or None,
                request.description or None,
                datetime.utcnow().isoformat()
            ))
            
            result = cur.fetchone()
            if result:
                project_id = result['id']
                
                cur.execute("""
                    INSERT INTO project_members (project_id, user_id, joined_at)
                    VALUES (%s, %s, %s)
                """, (project_id, request.owner_id, datetime.utcnow().isoformat()))
                
                return {
                    "id": result['id'],
                    "name": result['name'],
                    "owner_id": result['owner_id'],
                    "color": result['color'],
                    "description": result['description'],
                    "created_at": result['created_at'],
                    "active": result['active']
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to create project")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")


@router.get("/projects")
async def get_user_projects(user_id: int):
    """Получить список проектов пользователя"""
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        projects = user_repository.get_user_projects(user_id)
        return {
            "projects": projects,
            "count": len(projects)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching projects: {str(e)}")


@router.get("/user-projects")
async def get_user_projects_alias(user_id: int):
    """Alias для совместимости - получить список проектов пользователя"""
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        projects = user_repository.get_user_projects(user_id)
        return {
            "projects": projects,
            "count": len(projects)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching projects: {str(e)}")


@router.get("/project")
async def get_project(id: int):
    """Получить информацию о конкретном проекте"""
    try:
        if not id:
            raise HTTPException(status_code=400, detail="id is required")
        
        project = user_repository.get_project_by_id(id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching project: {str(e)}")


@router.get("/project/members")
async def get_project_members(id: int):
    """Получить список участников проекта"""
    try:
        if not id:
            raise HTTPException(status_code=400, detail="id is required")
        
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT pm.user_id, u.first_name, u.username, pm.joined_at
                FROM project_members pm
                LEFT JOIN users u ON pm.user_id = u.id
                WHERE pm.project_id = %s
                ORDER BY pm.joined_at ASC
            """, (id,))
            results = cur.fetchall()
            
            members = [
                {
                    'user_id': row['user_id'],
                    'first_name': row['first_name'],
                    'username': row['username'],
                    'joined_at': row['joined_at']
                }
                for row in results
            ]
            
            return members
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching project members: {str(e)}")


@router.post("/project/invite")
async def invite_project_member(request: InviteRequest):
    """Добавить участника в проект"""
    try:
        project_id = request.project_id
        user_id = request.user_id
        
        if not project_id or not user_id:
            raise HTTPException(status_code=400, detail="project_id and user_id are required")
        
        # Проверяем, существует ли проект
        project = user_repository.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Добавляем участника в проект
        with get_db_cursor() as cur:
            # Сначала проверяем, не является ли user_id telegram_id
            db_user_id = user_repository.resolve_user_id(user_id)
            if not db_user_id:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Проверяем, не добавлен ли уже
            cur.execute("""
                SELECT 1 FROM project_members 
                WHERE project_id = %s AND user_id = %s
            """, (project_id, db_user_id))
            
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="User already a member of this project")
            
            # Добавляем участника
            from datetime import datetime
            cur.execute("""
                INSERT INTO project_members (project_id, user_id, joined_at)
                VALUES (%s, %s, %s)
            """, (project_id, db_user_id, datetime.utcnow().isoformat()))
            
            return {
                "status": "success",
                "message": "User added to project",
                "project_id": project_id,
                "user_id": db_user_id
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding project member: {str(e)}")


@router.put("/project")
async def update_project(id: int, request: UpdateProjectRequest):
    """Обновить проект"""
    try:
        if not id:
            raise HTTPException(status_code=400, detail="id is required")
        
        if not request.name:
            raise HTTPException(status_code=400, detail="name is required")
        
        with get_db_cursor() as cur:
            cur.execute("""
                UPDATE projects 
                SET name = %s, color = %s, description = %s
                WHERE id = %s
                RETURNING id, name, owner_id, color, description, created_at, active
            """, (request.name, request.color or None, request.description or None, id))
            
            result = cur.fetchone()
            if result:
                return {
                    "id": result['id'],
                    "name": result['name'],
                    "owner_id": result['owner_id'],
                    "color": result['color'],
                    "description": result['description'],
                    "created_at": result['created_at'],
                    "active": result['active']
                }
            else:
                raise HTTPException(status_code=404, detail="Project not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")


@router.post("/project/member/remove")
async def remove_project_member(request: RemoveMemberRequest):
    """Удалить участника из проекта"""
    try:
        project_id = request.project_id
        user_id = request.user_id
        
        if not project_id or not user_id:
            raise HTTPException(status_code=400, detail="project_id and user_id are required")
        
        with get_db_cursor() as cur:
            cur.execute("""
                DELETE FROM project_members
                WHERE project_id = %s AND user_id = %s
            """, (project_id, user_id))
            
            return {
                "status": "success",
                "message": "Member removed from project",
                "project_id": project_id,
                "user_id": user_id
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing project member: {str(e)}")