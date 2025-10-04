#!/usr/bin/env python3
"""
Облачный сервер для Family Habits WebApp
Оптимизированный для работы на Render, Railway, Heroku
"""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию в Python path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn

# Получаем порт из переменной окружения (для облачных платформ)
PORT = int(os.environ.get("PORT", 8000))
HOST = "0.0.0.0"  # Обязательно для облачного хостинга

app = FastAPI(
    title="Family Habits WebApp",
    description="Telegram WebApp для семейного трекинга привычек",
    version="1.0.0"
)

# CORS для Telegram WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web.telegram.org", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
app.mount("/static", StaticFiles(directory="webapp"), name="static")

@app.get("/health")
async def health_check():
    """Health check для облачных платформ"""
    return {"status": "healthy", "message": "Family Habits WebApp is running"}

@app.get("/")
async def serve_index():
    """Главная страница"""
    return FileResponse("webapp/index.html")

@app.get("/registration")
async def serve_registration():
    return FileResponse("webapp/registration.html")

@app.get("/registration-children")
async def serve_registration_children():
    return FileResponse("webapp/registration-children.html")

@app.get("/welcome")
async def serve_welcome():
    return FileResponse("webapp/welcome.html")

@app.get("/create-task")
async def serve_create_task():
    return FileResponse("webapp/create-task.html")

@app.get("/shop")
async def serve_shop():
    return FileResponse("webapp/shop.html")

@app.get("/profile")
async def serve_profile():
    return FileResponse("webapp/profile.html")

@app.get("/statistics")
async def serve_statistics():
    return FileResponse("webapp/statistics.html")

@app.post("/api/telegram-data")
async def handle_telegram_data(request: Request):
    """Обработка данных от Telegram WebApp"""
    data = await request.json()
    # Здесь можно добавить обработку данных от Telegram
    return {"status": "success", "received": data}

if __name__ == "__main__":
    print(f"🚀 Запуск Family Habits WebApp на {HOST}:{PORT}")
    print(f"📱 WebApp доступен по адресу: http://{HOST}:{PORT}")
    
    uvicorn.run(
        "cloud_server:app",
        host=HOST,
        port=PORT,
        reload=False,  # Отключаем reload для продакшена
        access_log=True
    )