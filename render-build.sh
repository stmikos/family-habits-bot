#!/bin/bash

# Обновляем pip
python -m pip install --upgrade pip

# Устанавливаем только необходимые пакеты без проблемных зависимостей
pip install --no-cache-dir -r requirements-cloud.txt

# Проверяем что все установлено
python -c "import fastapi; import uvicorn; print('✅ FastAPI и uvicorn установлены успешно')"

echo "🎉 Сборка завершена успешно!"