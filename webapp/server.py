#!/usr/bin/env python3
"""
FastAPI server для обслуживания Family Habits WebApp
Интеграция с Telegram WebApp API
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="Family Habits WebApp",
    description="Семейный трекер привычек - веб-приложение для Telegram",
    version="1.0.0"
)

# CORS для Telegram WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web.telegram.org", "https://telegram.org", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Путь к статическим файлам
webapp_dir = Path(__file__).parent
static_dir = webapp_dir

@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница - оптимизированная для Telegram WebApp"""
    return FileResponse(static_dir / "index-telegram.html")

@app.get("/health")
async def health_check():
    """Проверка состояния сервера"""
    return {"status": "ok", "message": "Family Habits WebApp is running"}

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """Тестовая страница для диагностики"""
    return FileResponse(static_dir / "test.html")

@app.get("/test.html", response_class=HTMLResponse)
async def test_page_html():
    """Тестовая страница для диагностики"""
    return FileResponse(static_dir / "test.html")

@app.get("/index.html", response_class=HTMLResponse)
async def index_page():
    """Главная страница приложения"""
    return FileResponse(static_dir / "index.html")

@app.get("/registration.html", response_class=HTMLResponse)
async def registration_page():
    """Страница регистрации семьи"""
    return FileResponse(static_dir / "registration-new.html")

@app.get("/registration", response_class=HTMLResponse)
async def registration_page_short():
    """Страница регистрации семьи (короткий URL)"""
    return FileResponse(static_dir / "registration-new.html")

@app.get("/registration-children.html", response_class=HTMLResponse)
async def registration_children_page():
    """Страница добавления детей"""
    return FileResponse(static_dir / "registration-children.html")

@app.get("/welcome.html", response_class=HTMLResponse)
async def welcome_page():
    """Страница приветствия после регистрации"""
    return FileResponse(static_dir / "welcome.html")

@app.get("/welcome", response_class=HTMLResponse)
async def welcome_page_short():
    """Страница приветствия после регистрации (короткий URL)"""
    return FileResponse(static_dir / "welcome.html")

@app.get("/create-task.html", response_class=HTMLResponse)
async def create_task_page():
    """Страница создания задач"""
    return FileResponse(static_dir / "create-task.html")

@app.get("/shop.html", response_class=HTMLResponse)
async def shop_page():
    """Страница магазина наград"""
    return FileResponse(static_dir / "shop.html")

@app.get("/profile.html", response_class=HTMLResponse)
async def profile_page():
    """Страница профиля пользователя"""
    return FileResponse(static_dir / "profile.html")

@app.get("/statistics.html", response_class=HTMLResponse)
async def statistics_page():
    """Страница статистики"""
    return FileResponse(static_dir / "statistics.html")

@app.get("/design-system.css")
async def design_system_css():
    """CSS файл дизайн-системы"""
    return FileResponse(static_dir / "design-system.css", media_type="text/css")

# API эндпоинты для интеграции с Telegram Bot
@app.post("/api/telegram/user-data")
async def receive_telegram_data(request: Request):
    """Получение данных пользователя из Telegram WebApp"""
    try:
        data = await request.json()
        logger.info(f"Received Telegram data: {data}")
        
        # Здесь можно обработать данные пользователя
        # и синхронизировать с базой данных бота
        
        return {"status": "success", "message": "Data received"}
    except Exception as e:
        logger.error(f"Error processing Telegram data: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/tasks/create")
async def create_task_api(request: Request):
    """API для создания задач из WebApp"""
    try:
        data = await request.json()
        logger.info(f"Creating task: {data}")
        
        # Здесь будет логика создания задачи
        # Интеграция с базой данных бота
        
        return {"status": "success", "task_id": "demo_task_123"}
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/shop/purchase")
async def purchase_item_api(request: Request):
    """API для покупки товаров в магазине"""
    try:
        data = await request.json()
        logger.info(f"Purchase request: {data}")
        
        # Здесь будет логика покупки товаров
        # Проверка баланса звезд, списание, добавление в инвентарь
        
        return {"status": "success", "purchase_id": "demo_purchase_456"}
    except Exception as e:
        logger.error(f"Error processing purchase: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/user/{user_id}/stats")
async def get_user_stats(user_id: int):
    """Получение статистики пользователя"""
    try:
        # Здесь будет логика получения статистики из базы данных
        stats = {
            "user_id": user_id,
            "stars": 150,
            "level": 7,
            "streak_days": 12,
            "tasks_completed": 89,
            "family_participation": 85
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=404, detail="User not found")

if __name__ == "__main__":
    import uvicorn
    
    # Проверяем, что мы в правильной директории
    if not (static_dir / "index.html").exists():
        logger.error("index.html not found! Make sure you're running from webapp directory")
        exit(1)
    
    logger.info("🌱 Starting Family Habits WebApp Server...")
    logger.info(f"📁 Static files from: {static_dir}")
    logger.info("🔗 Telegram WebApp integration enabled")
    
    # Запускаем сервер
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )