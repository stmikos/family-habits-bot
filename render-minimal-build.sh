#!/bin/bash

echo "🔧 Запуск минимальной сборки для Render..."

# Обновляем pip
python -m pip install --upgrade pip

# Пробуем установить минимальные пакеты
echo "📦 Устанавливаем FastAPI и uvicorn..."
pip install --no-cache-dir fastapi==0.104.1
pip install --no-cache-dir uvicorn==0.24.0

# Проверяем установку
python -c "
try:
    import fastapi
    import uvicorn
    print('✅ Все пакеты установлены успешно!')
except ImportError as e:
    print(f'❌ Ошибка импорта: {e}')
    exit(1)
"

echo "🎉 Минимальная сборка завершена!"