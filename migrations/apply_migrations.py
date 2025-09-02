#!/usr/bin/env python3
"""
Helper script to apply all pending DB migrations on the server during deploy.
"""
import os
from migrations.migration_manager import MigrationManager

# Try to use DATABASE_URL from environment; fallback to app settings
try:
    from app.core.config import settings
    DEFAULT_DB_URL = settings.DATABASE_URL
except Exception:
    DEFAULT_DB_URL = None

def main():
    database_url = os.getenv("DATABASE_URL") or DEFAULT_DB_URL
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set and settings.DATABASE_URL is unavailable")
    mgr = MigrationManager(database_url)
    ok = mgr.migrate()
    if not ok:
        raise SystemExit(1)

if __name__ == "__main__":
    main()