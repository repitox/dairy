# Makefile для проекта Dialist

.PHONY: help install test lint format clean docker-build docker-up docker-down docker-test

# Переменные
PYTHON = python3
PIP = pip3
PYTEST = pytest
BLACK = black
FLAKE8 = flake8

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	$(PIP) install -r requirements.txt

install-dev: ## Установить зависимости для разработки
	$(PIP) install -r requirements-test.txt

test: ## Запустить тесты
	$(PYTEST) -v --cov=app --cov-report=term-missing

test-html: ## Запустить тесты с HTML отчетом
	$(PYTEST) -v --cov=app --cov-report=html --cov-report=term-missing

lint: ## Проверить код линтером
	$(FLAKE8) app/ tests/

format: ## Отформатировать код
	$(BLACK) app/ tests/

format-check: ## Проверить форматирование
	$(BLACK) --check app/ tests/

clean: ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

# Docker команды
docker-build: ## Собрать Docker образ
	docker-compose -f docker-compose.new.yml build

docker-up: ## Запустить приложение в Docker
	docker-compose -f docker-compose.new.yml up -d app-new db adminer

docker-down: ## Остановить Docker контейнеры
	docker-compose -f docker-compose.new.yml down

docker-test: ## Запустить тесты в Docker
	docker-compose -f docker-compose.new.yml --profile testing up --build test

docker-logs: ## Показать логи Docker
	docker-compose -f docker-compose.new.yml logs -f app-new

docker-shell: ## Открыть shell в Docker контейнере
	docker-compose -f docker-compose.new.yml exec app-new bash

docker-clean: ## Очистить Docker данные
	docker-compose -f docker-compose.new.yml down -v
	docker system prune -f

# Разработка
dev: ## Запустить приложение для разработки
	$(PYTHON) main_refactored.py

dev-old: ## Запустить старое приложение
	$(PYTHON) bot.py

# Проверки качества кода
quality: lint format-check test ## Полная проверка качества кода

# CI/CD
ci: install-dev quality ## Команды для CI/CD

# Миграции
migrate: ## Запустить миграции БД
	$(PYTHON) -c "from app.database.init import initialize_database; initialize_database()"