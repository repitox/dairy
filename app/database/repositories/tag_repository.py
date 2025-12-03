"""
Репозиторий для работы с тегами
"""
from app.database.connection import get_db_connection
from app.database.models.tag import Tag, TagAssociation
from datetime import datetime


class TagRepository:
    """Репозиторий для управления тегами"""

    @staticmethod
    def create_tag(tag: Tag) -> Tag:
        """Создать новый тег"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                tag.created_at = tag.created_at or datetime.now().isoformat()
                cur.execute(
                    """
                    INSERT INTO tags (name, background_color, project_id, created_by_id, created_at, active)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, name, background_color, project_id, created_by_id, created_at, active
                    """,
                    (tag.name, tag.background_color, tag.project_id, tag.created_by_id, tag.created_at, tag.active)
                )
                result = cur.fetchone()
                conn.commit()
                if result:
                    tag.id = result['id']
                    return tag
        return None

    @staticmethod
    def get_tag(tag_id: int) -> Tag:
        """Получить тег по ID"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, background_color, project_id, created_by_id, created_at, active
                    FROM tags
                    WHERE id = %s
                    """,
                    (tag_id,)
                )
                result = cur.fetchone()
                if result:
                    return Tag(
                        id=result['id'],
                        name=result['name'],
                        background_color=result['background_color'],
                        project_id=result['project_id'],
                        created_by_id=result['created_by_id'],
                        created_at=result['created_at'],
                        active=result['active']
                    )
        return None

    @staticmethod
    def get_project_tags(project_id: int, active_only: bool = True) -> list:
        """Получить все теги проекта"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT id, name, background_color, project_id, created_by_id, created_at, active
                    FROM tags
                    WHERE project_id = %s
                """
                params = [project_id]
                
                if active_only:
                    query += " AND active = TRUE"
                
                query += " ORDER BY created_at DESC"
                
                cur.execute(query, params)
                results = cur.fetchall()
                
                tags = []
                for row in results:
                    tag = Tag(
                        id=row['id'],
                        name=row['name'],
                        background_color=row['background_color'],
                        project_id=row['project_id'],
                        created_by_id=row['created_by_id'],
                        created_at=row['created_at'],
                        active=row['active']
                    )
                    tags.append(tag)
                return tags
        return []

    @staticmethod
    def update_tag(tag: Tag) -> bool:
        """Обновить тег"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE tags
                    SET name = %s, background_color = %s, active = %s
                    WHERE id = %s AND project_id = %s
                    """,
                    (tag.name, tag.background_color, tag.active, tag.id, tag.project_id)
                )
                conn.commit()
                return cur.rowcount > 0

    @staticmethod
    def delete_tag(tag_id: int) -> bool:
        """Удалить тег"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tags WHERE id = %s", (tag_id,))
                conn.commit()
                return cur.rowcount > 0

    @staticmethod
    def check_tag_exists(project_id: int, name: str, exclude_id: int = None) -> bool:
        """Проверить, существует ли тег с таким названием в проекте"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = "SELECT COUNT(*) as count FROM tags WHERE project_id = %s AND name = %s"
                params = [project_id, name]
                
                if exclude_id:
                    query += " AND id != %s"
                    params.append(exclude_id)
                
                cur.execute(query, params)
                result = cur.fetchone()
                return result['count'] > 0 if result else False


class TagAssociationRepository:
    """Репозиторий для управления связями тегов с объектами"""

    @staticmethod
    def add_tag_to_object(tag_id: int, object_type: str, object_id: int) -> TagAssociation:
        """Добавить тег к объекту"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                created_at = datetime.now().isoformat()
                cur.execute(
                    """
                    INSERT INTO tag_associations (tag_id, object_type, object_id, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (tag_id, object_type, object_id) DO NOTHING
                    RETURNING id
                    """,
                    (tag_id, object_type, object_id, created_at)
                )
                result = cur.fetchone()
                conn.commit()
                if result:
                    return TagAssociation(
                        id=result['id'],
                        tag_id=tag_id,
                        object_type=object_type,
                        object_id=object_id,
                        created_at=created_at
                    )
        return None

    @staticmethod
    def remove_tag_from_object(tag_id: int, object_type: str, object_id: int) -> bool:
        """Удалить тег от объекта"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM tag_associations
                    WHERE tag_id = %s AND object_type = %s AND object_id = %s
                    """,
                    (tag_id, object_type, object_id)
                )
                conn.commit()
                return cur.rowcount > 0

    @staticmethod
    def get_object_tags(object_type: str, object_id: int) -> list:
        """Получить все теги объекта"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT t.id, t.name, t.background_color, t.project_id, t.created_by_id, t.created_at, t.active
                    FROM tags t
                    JOIN tag_associations ta ON t.id = ta.tag_id
                    WHERE ta.object_type = %s AND ta.object_id = %s AND t.active = TRUE
                    ORDER BY t.created_at DESC
                    """,
                    (object_type, object_id)
                )
                results = cur.fetchall()
                
                tags = []
                for row in results:
                    tag = Tag(
                        id=row['id'],
                        name=row['name'],
                        background_color=row['background_color'],
                        project_id=row['project_id'],
                        created_by_id=row['created_by_id'],
                        created_at=row['created_at'],
                        active=row['active']
                    )
                    tags.append(tag)
                return tags
        return []

    @staticmethod
    def get_objects_by_tag(tag_id: int) -> list:
        """Получить все объекты с данным тегом"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, object_type, object_id, created_at
                    FROM tag_associations
                    WHERE tag_id = %s
                    """,
                    (tag_id,)
                )
                results = cur.fetchall()
                
                associations = []
                for row in results:
                    assoc = TagAssociation(
                        id=row['id'],
                        tag_id=tag_id,
                        object_type=row['object_type'],
                        object_id=row['object_id'],
                        created_at=row['created_at']
                    )
                    associations.append(assoc)
                return associations
        return []

    @staticmethod
    def clear_object_tags(object_type: str, object_id: int) -> bool:
        """Удалить все теги от объекта"""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM tag_associations
                    WHERE object_type = %s AND object_id = %s
                    """,
                    (object_type, object_id)
                )
                conn.commit()
                return cur.rowcount > 0
