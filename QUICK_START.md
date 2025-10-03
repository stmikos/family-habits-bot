# 🚀 Запуск Family Habits в Telegram

## ✅ Текущий статус

🌐 **WebApp работает локально:** http://localhost:8000
🤖 **Telegram Bot:** Настроен, ждет валидного токена

## 🔧 Финальная настройка

### 1. Проверьте токен бота
Убедитесь, что токен в `.env` файле активен:
```
TELEGRAM_BOT_TOKEN=ваш_активный_токен_от_BotFather
```

### 2. Создайте публичный URL (выберите один вариант):

#### Вариант A: ngrok (бесплатно)
```bash
# Зарегистрируйтесь на https://ngrok.com
ngrok config add-authtoken ваш_токен_ngrok
ngrok http 8000
```

#### Вариант B: Render/Railway (бесплатный хостинг)
1. Загрузите проект на GitHub
2. Подключите к Render/Railway
3. Укажите команду запуска: `cd webapp && python server.py`

#### Вариант C: Codespaces URL (если используете GitHub Codespaces)
Ваш URL будет в формате: `https://название-кодспейса-8000.app.github.dev`

### 3. Обновите .env
```
WEBAPP_URL=https://ваш-публичный-url.com
```

### 4. Настройте WebApp в боте
1. Откройте @BotFather
2. Выберите вашего бота
3. `/setmenubutton` → `@ваш_бот`
4. Введите:
   - **Текст:** `🌱 Family Habits`
   - **URL:** ваш публичный URL

### 5. Запустите бота
```bash
cd /workspaces/family-habits-bot
python -m app.bot.main
```

## 🎯 Тестирование

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Нажмите кнопку "🌱 Family Habits"
4. Наслаждайтесь полнофункциональным семейным трекером!

## 📱 Доступные команды

- `/app` - Открыть главное приложение
- `/family` - Семейная панель
- `/tasks` - Создать задачу  
- `/shop` - Магазин наград
- `/profile` - Профиль
- `/stats` - Статистика

## 🎊 Готово!

Family Habits полностью готов к использованию! Все 8 страниц WebApp интегрированы с Telegram Bot API.

---

*Хабит и Хабби готовы помочь вашей семье! 🌱*