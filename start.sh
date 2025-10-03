#!/bin/bash

# Family Habits Bot + WebApp Launcher
# Скрипт для запуска бота и веб-приложения

echo "🌱 Family Habits - Telegram Bot + WebApp"
echo "========================================="

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден! Установите Python 3.8+"
    exit 1
fi

# Проверяем, что мы в правильной директории
if [ ! -f "run_bot.py" ]; then
    echo "❌ Запустите скрипт из корня проекта family-habits-bot/"
    exit 1
fi

# Устанавливаем зависимости если нужно
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

echo "📦 Активация виртуального окружения..."
source venv/bin/activate

echo "📦 Установка основных зависимостей..."
pip install -q -r requirements.txt

echo "📦 Установка зависимостей для WebApp..."
pip install -q -r webapp/requirements.txt

# Проверяем .env файл
if [ ! -f ".env" ]; then
    echo "⚙️ Создание .env файла..."
    cat > .env << EOL
# Database
DATABASE_URL=sqlite+aiosqlite:///./family_habits.db
DATABASE_URL_SYNC=sqlite:///./family_habits.db

# Telegram Bot
TELEGRAM_BOT_TOKEN=demo_token_for_testing
WEBAPP_URL=http://localhost:8000

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000
EOL
fi

# Функция для остановки процессов
cleanup() {
    echo ""
    echo "🛑 Остановка сервисов..."
    if [ ! -z "$WEBAPP_PID" ]; then
        kill $WEBAPP_PID 2>/dev/null
    fi
    if [ ! -z "$BOT_PID" ]; then
        kill $BOT_PID 2>/dev/null
    fi
    exit 0
}

# Перехватываем Ctrl+C
trap cleanup SIGINT

echo ""
echo "🚀 Запуск Family Habits..."
echo ""

# Запускаем WebApp сервер
echo "🌐 Запуск WebApp сервера (порт 8000)..."
cd webapp
python3 server.py &
WEBAPP_PID=$!
cd ..

# Ждем запуска веб-сервера
sleep 3

# Проверяем, что веб-сервер запустился
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Ошибка запуска WebApp сервера!"
    kill $WEBAPP_PID 2>/dev/null
    exit 1
fi

echo "✅ WebApp сервер запущен: http://localhost:8000"

# Обновляем WEBAPP_URL в .env
sed -i 's|WEBAPP_URL=.*|WEBAPP_URL=http://localhost:8000|' .env

echo ""
echo "🤖 Запуск Telegram Bot..."

# Запускаем бота
python3 run_bot.py &
BOT_PID=$!

echo ""
echo "✅ Все сервисы запущены!"
echo ""
echo "📱 Telegram WebApp: http://localhost:8000"
echo "🌐 Все страницы:"
echo "   • Главная:      http://localhost:8000/index.html"
echo "   • Регистрация:  http://localhost:8000/registration.html"
echo "   • Создание задач: http://localhost:8000/create-task.html"
echo "   • Магазин:      http://localhost:8000/shop.html"
echo "   • Профиль:      http://localhost:8000/profile.html"
echo "   • Статистика:   http://localhost:8000/statistics.html"
echo ""
echo "🔧 Настройка Telegram Bot:"
echo "   1. Получите токен у @BotFather"
echo "   2. Установите TELEGRAM_BOT_TOKEN в .env"
echo "   3. Добавьте URL WebApp в бота: http://localhost:8000"
echo ""
echo "🛑 Для остановки нажмите Ctrl+C"
echo ""

# Ждем сигнала остановки
wait