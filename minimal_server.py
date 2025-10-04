#!/usr/bin/env python3
"""
Ультра минимальный сервер только для FastAPI (NO DEPENDENCIES!)
"""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

PORT = int(os.environ.get("PORT", 8000))
HOST = "0.0.0.0"

app = FastAPI(title="Family Habits WebApp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def home():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌱 Family Habits</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                padding: 20px; 
                background: linear-gradient(135deg, #2E7D32, #4CAF50);
                color: white;
                text-align: center;
            }
            .container { max-width: 400px; margin: 0 auto; }
            .mascot { font-size: 4em; margin: 20px 0; }
            .title { font-size: 2em; margin: 20px 0; }
            .btn { 
                background: #fff; 
                color: #2E7D32; 
                padding: 15px 30px; 
                border: none; 
                border-radius: 25px; 
                font-size: 1.1em; 
                margin: 10px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="mascot">🌱</div>
            <h1 class="title">Family Habits</h1>
            <p>Добро пожаловать в семейный трекер привычек!</p>
            <button class="btn" onclick="startApp()">Начать</button>
            
            <script>
                function startApp() {
                    if (window.Telegram && window.Telegram.WebApp) {
                        Telegram.WebApp.ready();
                        Telegram.WebApp.MainButton.text = "Готов!";
                        Telegram.WebApp.MainButton.show();
                    }
                    alert("🎉 Family Habits готов к работе!");
                }
                
                // Telegram WebApp инициализация
                if (window.Telegram && window.Telegram.WebApp) {
                    Telegram.WebApp.ready();
                    Telegram.WebApp.expand();
                }
            </script>
        </div>
    </body>
    </html>
    """)

if __name__ == "__main__":
    print(f"🚀 Минимальный сервер запущен на {HOST}:{PORT}")
    uvicorn.run("minimal_server:app", host=HOST, port=PORT)