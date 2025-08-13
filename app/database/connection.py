"""
Подключение к базе данных
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from app.core.config import settings

def get_conn():
    """Получить подключение к БД"""
    return psycopg2.connect(settings.DATABASE_URL, cursor_factory=RealDictCursor)

@contextmanager
def get_db_connection():
    """Контекстный менеджер для работы с БД"""
    conn = None
    try:
        conn = get_conn()
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_cursor():
    """Контекстный менеджер для работы с курсором БД"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            yield cur