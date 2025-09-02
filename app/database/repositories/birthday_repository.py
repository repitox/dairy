"""
Репозиторий для работы с днями рождения
"""
from typing import List, Optional, Tuple
from datetime import datetime

from app.database.connection import get_db_cursor
from app.database.repositories.user_repository import user_repository


class BirthdayRepository:
    def create_birthday(
        self,
        user_id: int,
        full_name: str,
        day: int,
        month: int,
        year: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Optional[int]:
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return None
        with get_db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO birthdays (user_id, full_name, day, month, year, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (db_user_id, full_name, day, month, year, description, datetime.utcnow().isoformat()),
            )
            row = cur.fetchone()
            return row["id"] if row else None

    def get_birthday(self, user_id: int, birthday_id: int) -> Optional[dict]:
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return None
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT * FROM birthdays WHERE id = %s AND user_id = %s",
                (birthday_id, db_user_id),
            )
            return cur.fetchone()

    def get_birthdays(self, user_id: int, limit: int, offset: int) -> List[dict]:
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return []
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT * FROM birthdays WHERE user_id = %s",
                (db_user_id,),
            )
            return cur.fetchall()

    def count_birthdays(self, user_id: int) -> int:
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return 0
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM birthdays WHERE user_id = %s",
                (db_user_id,),
            )
            row = cur.fetchone()
            return int(row["cnt"]) if row else 0

    def update_birthday(
        self,
        user_id: int,
        birthday_id: int,
        full_name: str,
        day: int,
        month: int,
        year: Optional[int],
        description: Optional[str],
    ) -> bool:
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return False
        with get_db_cursor() as cur:
            cur.execute(
                """
                UPDATE birthdays
                SET full_name = %s, day = %s, month = %s, year = %s, description = %s
                WHERE id = %s AND user_id = %s
                """,
                (full_name, day, month, year, description, birthday_id, db_user_id),
            )
            return cur.rowcount > 0

    def delete_birthday(self, user_id: int, birthday_id: int) -> bool:
        db_user_id = user_repository.resolve_user_id(user_id)
        if not db_user_id:
            return False
        with get_db_cursor() as cur:
            cur.execute(
                "DELETE FROM birthdays WHERE id = %s AND user_id = %s",
                (birthday_id, db_user_id),
            )
            return cur.rowcount > 0


birthday_repository = BirthdayRepository()

