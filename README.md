# Family Habits Bot

Telegram bot для семейного трекинга привычек и заданий с игровой механикой.

## 🎯 Описание

Family Habits Bot помогает семьям формировать полезные привычки через систему заданий, очков и наград:
- **Родители** создают задания для детей
- **Дети** выполняют задания и зарабатывают очки и монеты
- **Монеты** можно потратить в магазине наград
- **Статистика** и **достижения** мотивируют к регулярному выполнению

## 🚀 Статус разработки

### ✅ M0 — База и миграции (завершено)
- SQLAlchemy модели
- Alembic миграции
- Async сессии
- Базовая конфигурация

### ✅ M1 — Основной поток задач (завершено)
- REST API endpoints: `/auth/me`, `/children`, `/tasks`, `/checkins`, `/points/balance`
- Telegram bot: `/start`, роли Parent/Child
- E2E тесты (7/7 passing)
- Domain services: TaskService, PointsService

### 🔄 M2 — Начисления и магазин (в процессе)
- ✅ Shop API: `/shop/items`, `/shop/purchase`, `/shop/inventory`
- ✅ ShopService с валидацией монет
- ✅ E2E тесты для магазина (8/8 passing)
- ✅ Bot handlers: меню для детей и родителей
- ✅ FSM для создания заданий
- ⚠️ API интеграция в боте (заглушки готовы)
- ⚠️ Уведомления о покупках

### 📋 M3 — Награды и напоминания (планируется)
- RewardRule: пороги → события награды
- CRON: ежедневные напоминания
- Админ API для управления товарами и правилами

## 🛠 Технологии

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Alembic
- **Bot:** aiogram 3.x
- **Database:** PostgreSQL (prod), SQLite (dev/test)
- **Testing:** pytest, pytest-asyncio, httpx
- **Other:** pydantic, loguru, asyncpg

## 📦 Установка

```bash
# Клонировать репозиторий
git clone https://github.com/stmikos/family-habits-bot.git
cd family-habits-bot

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env
# Отредактировать .env с вашими настройками

# Применить миграции
alembic upgrade head
```

## 🧪 Тестирование

```bash
# Все тесты
pytest

# E2E тесты
pytest tests/e2e/

# С покрытием
pytest --cov=app tests/
```

### Текущие результаты тестов
- ✅ E2E API tests: 7/7 passing
- ✅ Shop API tests: 8/8 passing
- ✅ Total: 15 tests passing

## 🏗 Архитектура

```
app/
├── api/              # FastAPI application
│   ├── routes/      # API endpoints
│   └── schemas.py   # Pydantic schemas
├── bot/             # Telegram bot
│   ├── handlers/    # Message handlers
│   └── main.py      # Bot entry point
├── core/            # Core configuration
│   ├── config.py    # Settings
│   ├── logging.py   # Logger setup
│   └── exceptions.py # Custom exceptions
├── db/              # Database layer
│   ├── models.py    # SQLAlchemy models
│   └── session.py   # DB session management
└── services/        # Business logic
    ├── task_service.py
    ├── points_service.py
    └── shop_service.py
```

## 📊 Модели данных

- **Family** — семья, группа родителей и детей
- **Parent** — родитель, создаёт задания
- **Child** — ребёнок, выполняет задания, имеет баланс очков и монет
- **Task** — задание с типом (text/photo/video), очками и монетами
- **CheckIn** — отметка выполнения задания
- **PointsLedger** — журнал начислений/списаний
- **ShopItem** — товар в магазине
- **Purchase** — покупка товара
- **RewardRule** — правило начисления наград (M3)

## 🤖 Команды бота

### Для родителей
- `/parent` — главное меню родителя
  - ➕ Создать задание (FSM диалог)
  - 📋 Задания на проверку
  - 👶 Управление детьми
  - 📊 Статистика

### Для детей
- `/child` — главное меню ребёнка
  - 📋 Мои задания
  - 🪙 Баланс очков и монет
  - 🛒 Магазин наград
  - 🎒 Мои покупки

## 📝 API Endpoints

### Auth
- `GET /api/v1/auth/me` — получить текущего пользователя

### Children
- `GET /api/v1/children` — список детей
- `POST /api/v1/children` — создать ребёнка

### Tasks
- `GET /api/v1/tasks` — список заданий
- `POST /api/v1/tasks` — создать задание
- `PATCH /api/v1/tasks/{id}/approve` — одобрить задание
- `PATCH /api/v1/tasks/{id}/reject` — отклонить задание

### CheckIns
- `POST /api/v1/checkins` — сдать задание

### Points
- `GET /api/v1/points/balance/{child_id}` — баланс ребёнка
- `GET /api/v1/points/ledger/{child_id}` — история начислений

### Shop (M2)
- `GET /api/v1/shop/items` — список товаров
- `POST /api/v1/shop/purchase` — купить товар
- `GET /api/v1/shop/inventory/{child_id}` — история покупок

## 🔧 Конфигурация

Основные переменные окружения (`.env`):

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/family_habits
DATABASE_URL_SYNC=postgresql://user:pass@localhost:5432/family_habits

# Telegram Bot
BOT_TOKEN=your_bot_token_here
WEBAPP_URL=https://your-miniapp-url.com

# API
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secret-key
ADMIN_IDS=123456789

# Logging
LOG_LEVEL=INFO
```

## 📖 Документация

- [Copilot Instructions](.github/copilot-instructions.md) — инструкции для AI-агентов
- [API Docs](http://localhost:8000/docs) — Swagger UI (при запущенном сервере)

## 🤝 Вклад

Проект находится в активной разработке. Pull requests приветствуются!

## 📄 Лицензия

MIT License

## 👨‍💻 Автор

stmikos
