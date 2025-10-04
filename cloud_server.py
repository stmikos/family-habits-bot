#!/usr/bin/env python3
"""
Минимальный облачный сервер для Family Habits WebApp
Оптимизированный для работы на Render, Railway, Heroku без Rust зависимостей
"""

import os
import json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
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

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"🔍 {request.method} {request.url}")
    response = await call_next(request)
    print(f"📤 Ответ: {response.status_code}")
    return response

# Проверяем наличие папки webapp
webapp_dir = Path("webapp")
if not webapp_dir.exists():
    print("⚠️  Папка webapp не найдена, создаем базовую структуру")
    webapp_dir.mkdir(exist_ok=True)

# Статические файлы
if webapp_dir.exists():
    app.mount("/static", StaticFiles(directory="webapp"), name="static")

@app.get("/health")
async def health_check():
    """Health check для облачных платформ"""
    return {"status": "healthy", "message": "Family Habits WebApp is running"}

@app.get("/")
async def serve_index():
    """Главная страница - оптимизированная для Telegram"""
    print("📱 Запрос главной страницы (Telegram WebApp)")
    try:
        return FileResponse("webapp/index-telegram.html")
    except Exception as e:
        print(f"❌ Ошибка загрузки index-telegram.html: {e}")
        # Fallback на обычную версию
        try:
            return FileResponse("webapp/index.html")
        except:
            return HTMLResponse("""
            <html><head><title>Family Habits</title></head>
            <body><h1>🌱 Family Habits WebApp</h1>
            <p>Откройте приложение через Telegram бота!</p></body></html>
            """)

@app.get("/registration")
async def serve_registration():
    print("📝 Запрос страницы регистрации")
    try:
        file_path = "webapp/registration-new.html"
        if not Path(file_path).exists():
            print(f"❌ Файл {file_path} не найден")
            return JSONResponse({"error": f"File {file_path} not found"}, status_code=404)
        print(f"✅ Отправляем файл {file_path}")
        return FileResponse(file_path)
    except Exception as e:
        print(f"❌ Ошибка загрузки registration: {e}")
        return JSONResponse({"error": f"Registration page error: {str(e)}"}, status_code=500)

@app.get("/registration-children")
async def serve_registration_children():
    try:
        return FileResponse("webapp/registration-children.html")
    except:
        return JSONResponse({"error": "File not found"}, status_code=404)

@app.get("/welcome")
async def serve_welcome():
    try:
        return FileResponse("webapp/welcome.html")
    except:
        return JSONResponse({"error": "File not found"}, status_code=404)

@app.get("/create-task")
async def serve_create_task():
    try:
        return FileResponse("webapp/create-task.html")
    except:
        return JSONResponse({"error": "File not found"}, status_code=404)

@app.get("/shop")
async def serve_shop():
    try:
        return FileResponse("webapp/shop.html")
    except:
        return JSONResponse({"error": "File not found"}, status_code=404)

@app.get("/profile")
async def serve_profile():
    try:
        return FileResponse("webapp/profile.html")
    except:
        return JSONResponse({"error": "File not found"}, status_code=404)

@app.get("/statistics")
async def serve_statistics():
    try:
        return FileResponse("webapp/statistics.html")
    except:
        return JSONResponse({"error": "File not found"}, status_code=404)

@app.post("/api/telegram-data")
async def handle_telegram_data(request: Request):
    """Обработка данных от Telegram WebApp"""
    try:
        data = await request.json()
        return {"status": "success", "received": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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