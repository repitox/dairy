---
description: Repository Information Overview
alwaysApply: true
---

# Telegram Bot Project Information

## Summary

Telegram-integrated task management and productivity system with dual interfaces: a web dashboard and mobile WebApp for Telegram. Backend built with Python FastAPI, frontend with vanilla HTML/CSS/JavaScript, connected to PostgreSQL database.

## Repository Structure

**Main Components:**
- **`app/`** - FastAPI backend (API routes, Telegram bot integration, database models, repositories)
- **`dashboard/`** - Web interface for browser access (90+ HTML pages with UI components)
- **`static/`** - Telegram WebApp static files (HTML, CSS, JavaScript)
- **`tests/`** - Pytest test suite with fixtures
- **`migrations/`** - Database migration scripts and tools
- **`docs/`** - Comprehensive documentation (150+ markdown files)
- **`blog/`** - Development journal/daily updates

## Language & Runtime

**Languages**: Python, HTML, CSS, JavaScript  
**Python Version**: 3.11-slim  
**Framework**: FastAPI  
**Package Manager**: pip  
**Build System**: Docker (multi-stage build)  
**Database**: PostgreSQL 15

## Dependencies

**Main Dependencies**:
- `python-telegram-bot==22.0` - Telegram bot client
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `psycopg2-binary` - PostgreSQL adapter
- `apscheduler` - Task scheduling
- `python-dotenv` - Environment variables
- `requests` - HTTP client
- `pytz` - Timezone handling

**Development Dependencies**:
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async test support
- `httpx>=0.24.0` - HTTP async client
- `pytest-cov>=4.0.0` - Coverage reporting

## Build & Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Development with test dependencies
pip install -r requirements-test.txt

# Docker build (development)
docker-compose -f docker-compose.new.yml build

# Docker run
docker-compose -f docker-compose.new.yml up -d app-new db adminer

# Local development
python main_refactored.py

# Database initialization
python -c "from app.database.init import initialize_database; initialize_database()"
```

## Docker

**Dockerfile**: `Dockerfile.new` (multi-stage build)  
**Base Image**: `python:3.11-slim`  
**Build Stages**:
- `base` - Common dependencies (PostgreSQL client, gcc)
- `development` - Includes test dependencies, mounts source code
- `production` - Stripped down, runs as non-root user
- `testing` - Runs pytest on container startup

**Docker Compose** (`docker-compose.yml`):
- `app` service (port 8000) - FastAPI application
- `db` service (port 5432) - PostgreSQL 15
- `adminer` service (port 8080) - Database management UI
- `test-db` & `test` services (testing profile)

## Main Entry Points

**Backend Startup**:
- `main_refactored.py` - FastAPI app initialization with Telegram webhook
- `start_server.py` - Development server with database auto-migration
- `app/main.py` - Creates FastAPI app, mounts static files, includes API routers

**Frontend Access**:
- `/dashboard/` - Web dashboard (mounted from `dashboard/` directory)
- `/webapp/` - Telegram WebApp (mounted from `static/` directory)

**API Routes** (all under `/api` prefix):
- `/auth` - Authentication
- `/tasks`, `/shopping`, `/events`, `/projects`, `/notes`
- `/dashboard`, `/navigation`, `/birthdays`

## Testing

**Framework**: Pytest  
**Test Location**: `tests/` directory  
**Configuration**: `pytest.ini`  
**Naming Convention**: `test_*.py` files with `Test*` classes and `test_*` functions

**Fixtures** (`conftest.py`):
- `app` - FastAPI test application
- `client` - AsyncClient for async tests
- `sync_client` - Synchronous TestClient
- Test data fixtures for users, tasks, events, birthdays, shopping items

**Coverage Requirements**: 80% minimum  
**Run Command**:

```bash
# Basic tests
pytest -v --cov=app --cov-report=term-missing

# With HTML report
pytest -v --cov=app --cov-report=html --cov-report=term-missing

# Docker tests
docker-compose -f docker-compose.new.yml --profile testing up --build test

# Makefile
make test
make test-html
```

## Quality & Code Standards

**Available Commands** (Makefile):
- `make lint` - Run flake8 on app/ and tests/
- `make format` - Format code with black
- `make format-check` - Check formatting without changes
- `make quality` - Run full quality checks (lint, format check, tests)
- `make clean` - Remove Python cache files and coverage data

**Markers** (pytest):
- `@pytest.mark.asyncio` - Async tests
- `@pytest.mark.slow` - Performance tests
- `@pytest.mark.integration` - Integration tests

## Configuration Files

- `.env.example` - Environment variables template (BOT_TOKEN, DATABASE_URL, DOMAIN, etc.)
- `app/core/config.py` - Application configuration
- `migrations/` - Database migration management scripts
- `docs/MIGRATION_SYSTEM.md` - Migration system documentation
- `docs/DEPLOY_TO_NETANGELS.md` - Production deployment instructions
