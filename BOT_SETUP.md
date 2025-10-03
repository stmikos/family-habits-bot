# 🤖 Настройка Telegram Bot

## Получение нового токена

1. Откройте Telegram и найдите @BotFather
2. Отправьте команду `/newbot`
3. Введите имя бота (например: "Family Habits")
4. Введите username бота (например: "family_habits_your_name_bot")
5. Скопируйте полученный токен

## Настройка WebApp

После получения токена:

1. Отправьте @BotFather команду `/setmenubutton`
2. Выберите вашего бота
3. Введите текст кнопки: `🌱 Family Habits`
4. Введите URL: `https://fictional-doodle-wr4vv65qv6qv3grv7-8000.app.github.dev`

## Обновление .env

Замените токен в файле `.env`:
```
TELEGRAM_BOT_TOKEN=ваш_новый_токен
```

## Запуск

```bash
cd /workspaces/family-habits-bot
python -m app.bot.main
```

---

**WebApp URL:** https://fictional-doodle-wr4vv65qv6qv3grv7-8000.app.github.dev

Этот URL уже настроен и работает! 🚀