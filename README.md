# 🌱 Family Habits Bot

**Telegram-бот для семейного трекинга привычек с WebApp интерфейсом**

Интерактивное приложение для создания и отслеживания семейных привычек с системой мотивации через виртуальный магазин наград.

## ✨ Основные функции

- 👨‍👩‍👧‍👦 **Семейная регистрация** - создание семейного аккаунта с детьми
- 📋 **Управление задачами** - создание привычек и отслеживание прогресса  
- 🏪 **Виртуальный магазин** - система наград за выполненные задачи
- 📊 **Статистика** - детальная аналитика прогресса семьи
- 👤 **Профили** - персональные страницы участников
- 🎨 **Красивый дизайн** - зеленая природная тема с маскотами Habit и Habby

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/stmikos/family-habits-bot.git
cd family-habits-bot
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
cd webapp && pip install -r requirements.txt && cd ..
```

### 3. Настройка переменных окружения
```bash
cp .env.example .env
# Отредактируйте .env файл, добавив ваш bot token
```

### 4. Запуск WebApp сервера
```bash
cd webapp
python server.py
```

### 5. Запуск Telegram бота
```bash
# В новом терминале
python -m app.bot.main
```

## 🔧 Настройка для GitHub Codespaces

1. **Получите URL Codespaces:**
```bash
echo "https://$CODESPACE_NAME-8000.app.github.dev"
```

2. **Обновите .env файл:**
```bash
WEBAPP_URL=https://your-codespace-name-8000.app.github.dev
```

3. **Настройте WebApp в @BotFather:**
   - Отправьте `/mybots` в @BotFather
   - Выберите вашего бота → Bot Settings → Menu Button → Edit menu button URL
   - Вставьте ваш Codespaces URL

## 📱 WebApp Страницы

- **Главная** (`/`) - регистрация и вход
- **Регистрация** (`/registration`) - создание семейного аккаунта
- **Дети** (`/registration-children`) - добавление детей в семью
- **Приветствие** (`/welcome`) - стартовая страница после регистрации
- **Создание задач** (`/create-task`) - добавление новых привычек
- **Магазин** (`/shop`) - покупка наград за монеты
- **Профиль** (`/profile`) - личная информация и настройки
- **Статистика** (`/statistics`) - графики и аналитика прогресса

## 🤖 Команды бота

- `/start` - запуск бота и инструкции
- `/app` - открыть главное приложение
- `/family` - управление семьей
- `/tasks` - создание задач
- `/shop` - виртуальный магазин
- `/profile` - личный профиль  
- `/stats` - статистика прогресса

## 🛠️ Технологический стек

- **Backend:** Python 3.9+, FastAPI, aiogram 3.x
- **Database:** SQLite с Alembic миграциями
- **Frontend:** HTML5, CSS3, JavaScript
- **WebApp API:** Telegram WebApp API
- **UI Framework:** Собственная дизайн-система
- **Charts:** Chart.js для статистики

## 📁 Структура проекта

```
family-habits-bot/
├── app/                    # Основное приложение
│   ├── bot/               # Telegram bot логика
│   ├── core/              # Конфигурация и настройки
│   ├── db/                # Модели базы данных
│   └── services/          # Бизнес логика
├── webapp/                # WebApp интерфейс
│   ├── *.html            # HTML страницы
│   ├── design-system.css # Система дизайна
│   ├── telegram-webapp.js # Telegram WebApp API
│   └── server.py         # FastAPI сервер
├── alembic/              # Миграции базы данных
├── tests/                # Тесты
└── docs/                 # Документация
```

## 🎨 Дизайн система

Приложение использует зеленую природную тему с:
- Основной цвет: `#2E7D32` (Forest Green)
- Акцентный: `#4CAF50` (Success Green)  
- Градиенты и тени для современного вида
- Маскоты Habit 🌱 и Habby 🍃
- Адаптивный дизайн для мобильных устройств

## 📖 Документация

- [BOT_SETUP.md](BOT_SETUP.md) - Подробная настройка бота
- [TELEGRAM_WEBAPP_GUIDE.md](TELEGRAM_WEBAPP_GUIDE.md) - Гайд по WebApp API
- [QUICK_START.md](QUICK_START.md) - Быстрый старт для разработки

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Проект распространяется под лицензией MIT. См. [LICENSE](LICENSE) для подробностей.

## 🆘 Поддержка

Если у вас возникли вопросы или проблемы:
1. Проверьте [Issues](https://github.com/stmikos/family-habits-bot/issues)
2. Создайте новый Issue с подробным описанием
3. Убедитесь, что следуете инструкциям в документации

---

**Создано с ❤️ для семей, которые хотят развивать полезные привычки вместе!**

## 🚀 Возможности M2

### ✅ Реализовано в M2:

- **🤖 Telegram Bot (aiogram 3.x)**
  - Роли: Родитель/Ребёнок
  - Автоматическая регистрация
  - Команды: `/start`, `/info`, `/stats`

- **📱 MiniApp Интеграция**
  - Кнопки WebApp для родителей и детей
  - URL настраиваются в `WEBAPP_URL`

- **📝 FSM Создание заданий**
  - 6-этапный диалог создания задания
  - Выбор ребёнка, название, описание, тип (текст/фото/видео)
  - Настройка очков и монет за выполнение

- **⭐ Система очков и монет**
  - Очки за выполнение заданий
  - Монеты для покупок в магазине
  - Журнал начислений `PointsLedger`

- **🛒 Магазин (основа)**
  - Модели `ShopItem`, `Purchase`
  - Демо-товары в базе данных

- **📊 База данных**
  - SQLAlchemy модели с Telegram интеграцией
  - Поля `tg_id` для связи с пользователями
  - Alembic миграции

## 🏗️ Архитектура

```
app/
├── bot/                    # Telegram Bot
│   ├── handlers/          # Обработчики команд
│   │   ├── start.py      # /start, роли, главное меню
│   │   ├── tasks.py      # FSM создание заданий
│   │   └── admin.py      # /info, /stats
│   ├── middlewares/      # Middleware
│   │   └── auth.py       # База данных, авторизация
│   └── main.py           # Dispatcher, запуск бота
├── db/                    # База данных
│   ├── models.py         # SQLAlchemy модели
│   └── session.py        # Async sessions
├── services/              # Бизнес-логика
│   ├── parent_service.py # Работа с родителями
│   └── task_service.py   # Работа с заданиями
└── core/                  # Конфигурация
    ├── config.py         # Настройки
    └── logging.py        # Логирование
```

## ⚙️ Установка и запуск

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка окружения

Создайте `.env`:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
WEBAPP_URL=https://your-miniapp-domain.com

# Database
DATABASE_URL=sqlite+aiosqlite:///./family_habits.db

# Admin
ADMIN_USER_IDS=123456789,987654321
```

### 3. Создание базы данных

```bash
alembic upgrade head
```

### 4. Запуск

```bash
# Демо (без реального Telegram)
python run_bot.py

# С реальным ботом
python -m app.bot.main
```

### 5. Тестирование

```bash
python test_bot.py
```

## 🎮 Использование

### Для родителей:

1. **Старт**: `/start` → автоматическая регистрация как родитель
2. **Главное меню**:
   - 🏠 **Семейная панель** (MiniApp)
   - 📝 **Создать задание** (FSM диалог)
   - 📊 **Статистика** / 👨‍👩‍👧‍👦 **Дети**

3. **Создание задания**:
   - Выбор ребёнка
   - Название и описание
   - Тип подтверждения (текст/фото/видео)
   - Очки и монеты за выполнение

### Для детей:

1. **Регистрация**: Родитель добавляет ребёнка, потом ребёнок пишет `/start`
2. **Главное меню**:
   - 🎮 **Мои задания** (MiniApp)
   - 🏆 **Мои очки**
   - 🛒 **Магазин**

## 📊 Модели данных

### Основные сущности:

- **`Family`** - семья (план FREE/PRO)
- **`Parent`** - родитель (связь с Telegram через `tg_id`)
- **`Child`** - ребёнок (очки, монеты, `tg_id` опционально)
- **`Task`** - задание (от родителя к ребёнку)
- **`CheckIn`** - сдача задания ребёнком
- **`PointsLedger`** - журнал начислений
- **`ShopItem`** - товар в магазине
- **`Purchase`** - покупка ребёнка

## 🔄 FSM Workflow

### Создание задания:

```
1. waiting_for_child    → Выбор ребёнка
2. waiting_for_title    → Название задания
3. waiting_for_description → Описание
4. waiting_for_type     → Тип (текст/фото/видео)
5. waiting_for_points   → Очки за выполнение
6. waiting_for_coins    → Монеты за выполнение
→ Создание Task, уведомление ребёнка
```

## 🔗 MiniApp Интеграция

Bot создаёт кнопки WebApp:

- **Родители**: `{WEBAPP_URL}/parent` - управление заданиями, семья
- **Дети**: `{WEBAPP_URL}/child` - просмотр заданий, магазин

MiniApp должно использовать существующий REST API (M1) для работы с данными.

## 📈 Следующие шаги (M3)

1. **🌐 MiniApp Frontend**
   - React/Vue/Vanilla JS интерфейс
   - Telegram WebApp SDK
   - Подключение к REST API

2. **🛒 Полная система магазина**
   - Корзина, оформление покупок
   - Уведомления родителей о покупках
   - Управление товарами

3. **📊 Аналитика и статистика**
   - Графики выполнения заданий
   - Прогресс детей
   - Семейная статистика

4. **🔔 Уведомления**
   - Новые задания для детей
   - Сдача заданий для родителей
   - Покупки в магазине

5. **🎯 Геймификация**
   - Достижения, бейджи
   - Рейтинги детей
   - Квесты и челленджи

## 🛠️ Разработка

### Структура проекта:

- **M0**: База данных, модели, сервисы
- **M1**: REST API FastAPI ✅ (7/7 E2E тестов)
- **M2**: Telegram Bot + MiniApp кнопки ✅
- **M3**: MiniApp Frontend (в разработке)

### Технологии:

- **Backend**: FastAPI, SQLAlchemy, Alembic
- **Bot**: aiogram 3.x, FSM
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Frontend**: React/Vue + Telegram WebApp SDK

---

**Status**: ✅ M2 Complete - Bot infrastructure ready for MiniApp integration