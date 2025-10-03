# 🌱 Family Habits - Telegram WebApp Integration

## ✅ Статус интеграции

**M2 фаза ЗАВЕРШЕНА!** Полная интеграция Telegram Bot + WebApp готова к использованию.

## 🚀 Что реализовано

### 🤖 Telegram Bot
- ✅ aiogram 3.x с WebApp интеграцией
- ✅ Команды для всех страниц приложения
- ✅ Кнопки WebApp для каждой функции
- ✅ Автоматическая регистрация пользователей
- ✅ Семейная система (Parent/Child)

### 🌐 WebApp Frontend
- ✅ 8 полностью функциональных страниц
- ✅ Telegram WebApp API интеграция
- ✅ Адаптивный дизайн для мобильных
- ✅ Зеленая природная тема с Хабит и Хабби
- ✅ Интерактивные элементы и анимации

### 🔗 Интеграция
- ✅ FastAPI сервер для WebApp
- ✅ CORS настройки для Telegram
- ✅ API эндпоинты для синхронизации данных
- ✅ Автоматическая передача пользовательских данных

## 📱 Доступные команды бота

| Команда | Описание | WebApp страница |
|---------|----------|----------------|
| `/app` или `/start` | Главное приложение | index.html |
| `/family` | Семейная панель | index.html?tab=family |
| `/tasks` | Создание задач | create-task.html |
| `/shop` | Магазин наград | shop.html |
| `/profile` | Профиль пользователя | profile.html |
| `/stats` | Статистика | statistics.html |

## 🛠️ Быстрый запуск

### 1. Запуск в демо-режиме (уже настроено)
```bash
# Терминал 1: WebApp сервер
cd /workspaces/family-habits-bot/webapp
python3 server.py

# Терминал 2: Telegram Bot
cd /workspaces/family-habits-bot
python3 run_bot.py
```

**Доступно сейчас:**
- 🌐 WebApp: http://localhost:8000
- 🤖 Bot: демо-режим (покажет инструкции)

### 2. Настройка реального Telegram бота

#### Шаг 1: Получить токен
1. Напишите @BotFather в Telegram
2. Создайте нового бота: `/newbot`
3. Скопируйте токен

#### Шаг 2: Настроить .env
```bash
# Замените в файле .env
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
WEBAPP_URL=https://ваш-домен.com  # или ngrok URL
```

#### Шаг 3: Настроить WebApp в боте
1. Откройте @BotFather
2. Выберите вашего бота
3. `/setmenubutton` → `@ваш_бот`
4. Введите:
   - **Текст кнопки:** `🌱 Family Habits`
   - **URL:** `https://ваш-домен.com`

#### Шаг 4: Запуск
```bash
# Автоматический запуск всех сервисов
./start.sh
```

## 🌍 Деплой в продакшн

### Опция 1: Render/Railway/Heroku
1. Создайте два приложения:
   - **Backend:** `/workspaces/family-habits-bot/webapp/`
   - **Bot:** `/workspaces/family-habits-bot/`

2. Переменные окружения:
```
TELEGRAM_BOT_TOKEN=ваш_токен
WEBAPP_URL=https://ваш-webapp.render.com
DATABASE_URL=postgres://...
```

### Опция 2: VPS/Cloud
1. Установите зависимости:
```bash
pip install -r requirements.txt
pip install -r webapp/requirements.txt
```

2. Настройте reverse proxy (nginx):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. Запустите с systemd или supervisor

## 📁 Структура файлов

```
/workspaces/family-habits-bot/
├── webapp/                          # WebApp Frontend
│   ├── server.py                   # FastAPI сервер
│   ├── telegram-webapp.js          # Telegram WebApp API
│   ├── design-system.css           # Дизайн-система
│   ├── index.html                  # Главная страница
│   ├── registration.html           # Регистрация семьи
│   ├── registration-children.html  # Добавление детей
│   ├── welcome.html                # Приветствие
│   ├── create-task.html            # Создание задач
│   ├── shop.html                   # Магазин наград
│   ├── profile.html                # Профиль
│   └── statistics.html             # Статистика
├── app/bot/handlers/webapp.py      # Telegram команды
├── start.sh                       # Автозапуск
└── .env                           # Настройки
```

## 🎯 Функциональность по страницам

### 🏠 **index.html** - Главная
- Дашборд семьи
- Быстрые действия
- Прогресс по задачам
- Статистика дня

### 👨‍👩‍👧‍👦 **registration.html** - Регистрация
- Создание семейного профиля
- Выбор роли (Родитель)
- Базовые настройки

### 👶 **registration-children.html** - Дети
- Добавление детей в семью
- Настройка аватаров
- Возраст и интересы

### 🎉 **welcome.html** - Приветствие
- Поздравление с регистрацией
- Быстрый старт
- Первые задачи

### ✅ **create-task.html** - Создание задач
- Шаблоны задач
- Настройка сложности
- Назначение исполнителей
- Система наград

### 🛍️ **shop.html** - Магазин
- Покупка наград за звезды
- Категории товаров
- Семейные развлечения
- История покупок

### 👤 **profile.html** - Профиль
- Статистика пользователя
- Достижения и уровни
- Управление семьей
- Настройки

### 📊 **statistics.html** - Аналитика
- Графики прогресса
- Семейный рейтинг
- Инсайты и рекомендации
- Экспорт данных

## 🔧 API Integration

### Эндпоинты WebApp
- `POST /api/telegram/user-data` - Получение данных пользователя
- `POST /api/tasks/create` - Создание задач
- `POST /api/shop/purchase` - Покупка товаров
- `GET /api/user/{user_id}/stats` - Статистика пользователя

### Sync с Telegram Bot
WebApp автоматически синхронизируется с базой данных бота через:
- Telegram WebApp API (initData)
- REST API эндпоинты
- Shared database

## 🐛 Отладка

### Проверка WebApp
```bash
curl http://localhost:8000/health
# Должен вернуть: {"status": "ok", "message": "Family Habits WebApp is running"}
```

### Проверка страниц
- ✅ http://localhost:8000/index.html
- ✅ http://localhost:8000/registration.html
- ✅ http://localhost:8000/shop.html

### Логи
- **WebApp:** uvicorn логи в терминале
- **Bot:** логи в файл `/workspaces/family-habits-bot/logs/`

## 🎊 Готово к использованию!

**Family Habits** полностью готов к использованию:
- 🤖 Telegram Bot с WebApp кнопками
- 🌐 Responsive WebApp с 8 страницами  
- 🔗 Полная интеграция через Telegram WebApp API
- 🎨 Дизайн с Хабит и Хабби талисманами
- 📱 Оптимизация для мобильных устройств

**Следующие шаги:** Получите токен у @BotFather и настройте продакшн деплой! 🚀