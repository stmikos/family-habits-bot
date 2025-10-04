# Настройка Telegram Bot на Render

## 📋 Необходимые шаги для работы бота в Telegram:

### 1. **Добавить переменные окружения на Render:**

Зайдите в настройки вашего сервиса на Render и добавьте:

```
TELEGRAM_BOT_TOKEN=8441861914:AAGa4MST7HY7TH75W8ENORjoq_CicvUrQWI
WEBAPP_URL=https://family-habits-bot.onrender.com
```

### 2. **Перезапустить сервис на Render**

После добавления переменных нажмите "Manual Deploy" для перезапуска.

### 3. **Проверить статус webhook:**

```bash
curl "https://api.telegram.org/bot8441861914:AAGa4MST7HY7TH75W8ENORjoq_CicvUrQWI/getWebhookInfo"
```

Должно показать:
```json
{
  "ok": true,
  "result": {
    "url": "https://family-habits-bot.onrender.com/telegram-webhook",
    "pending_update_count": 0
  }
}
```

### 4. **Тестирование:**

1. Найдите бота в Telegram: `@habbitquest_bot`
2. Отправьте команду `/start`
3. Должна появиться кнопка "🌱 Открыть Family Habits"
4. При нажатии откроется WebApp

## ✅ **Что исправлено:**

- ✅ Объединены WebApp и Bot в одном сервере
- ✅ Автоматическая установка webhook при запуске
- ✅ Обработка команд `/start` и `/app`
- ✅ Отправка WebApp кнопки пользователям
- ✅ Поддержка переменных окружения из .env

## 🔧 **Отладка:**

Если не работает, проверьте логи на Render:
- Должно быть: `✅ Webhook установлен: https://family-habits-bot.onrender.com/telegram-webhook`
- Должно быть: `🤖 Bot Token: ✅ Настроен`

## 📱 **Как использовать:**

1. Пользователь пишет `/start` боту
2. Бот отправляет сообщение с WebApp кнопкой
3. Пользователь нажимает кнопку
4. Открывается Family Habits WebApp в Telegram