# Family Habit — Tech Outline
Стек: Python 3.11, aiogram 3.x, FastAPI, Postgres (SQLAlchemy), Alembic, pydantic, pytest, uvicorn, loguru.

Модули:
- app/bot/ — Telegram-бот (aiogram): хендлеры parent/child, FSM, меню.
- app/api/ — FastAPI: webhooks, админ API, healthcheck.
- app/db/ — SQLAlchemy модели, сессии, Alembic миграции.
- app/core/ — конфиг, логирование, utils, exceptions.
- app/services/ — доменная логика: tasks, points, rewards, media.
- tests/ — pytest, factory-boy, e2e c httpx.

Требования к коду:
- type hints обязательны, pydantic-схемы на вход/выход API.
- все функции ≤ 40 строк, без магии, явные докстринги.
- тесты: на каждую публичную функцию — минимум 1 unit + 1 интеграционный на happy-path.