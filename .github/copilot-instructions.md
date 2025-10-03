# Copilot Prompt Cookbook — Family Habit

> Шпаргалка промтов и каркасов, чтобы GitHub Copilot стабильно генерил код без плясок с бубном. Вставляй как комментарии и докстринги прямо в файлы проекта.

---

## 0) Правила игры для Copilot (вставить в README.md)

* Пишем задачи **маленькими шагами**, каждый шаг — отдельный комментарий.
* Всегда показываем **контекст**: импорты, типы, примеры данных.
* Сначала **тест/интерфейс**, потом реализация.
* Фиксируем **словари терминов** (parent/child/task/quest/points).
* Любая неоднозначность — превращаем в список требований в комментарии.

```md
## Glossary
- Parent — родитель/опекун, владелец семейного аккаунта
- Child — ребёнок, исполнитель задач
- Task — задание с дедлайном, типом ответа (text/photo/video)
- Check-in — отметка выполнения задачи
- Reward — награда за достижения/очки
- Points — очки за выполнение (по умолчанию 5 за базовую задачу)
```

---

## 1) Каркас репозитория (вставить в корневой `COPILOT_BRIEF.md`)

```md
# Family Habit — Tech Outline
Стек: Python 3.11, aiogram 3.x, FastAPI, Postgres (SQLAlchemy), Alembic, pydantic, pytest, uvicorn, loguru.

Модули:
- app/bot/ — Telegram-бот (aiogram): хендлеры parent/child, FSM, меню.
- app/api/ — FastAPI: webhooks, админ API, healthcheck.
- app/db/ — SQLAlchemy модели, сессии, Alembic миграции.
- app/core/ — конфиг, логирование, utils, exceptions.
- app/services/ — доменная логика: tasks, points, rewards, media.
- tests/ — pytest, factory-boy, e2e c httpx.

Требования к коду:
- type hints обязательны, pydantic-схемы на вход/выход API.
- все функции ≤ 40 строк, без магии, явные докстринги.
- тесты: на каждую публичную функцию — минимум 1 unit + 1 интеграционный на happy-path.
```

---

## 2) Заголовок каждого файла — «бриф для Copilot»

```python
# Purpose: Реализовать доменную логику Family Habit.
# Context:
# - Есть роли Parent/Child. Parent создаёт Task, Child выполняет.
# - Task: title:str, description:str, type: Literal["text","photo","video"],
#         points:int=5, due_at:datetime | None, status: Literal["new","in_progress","done","approved","rejected"].
# - Check-in: вложение медиа, комментарий, время отправки.
# Requirements:
# 1) Написать функции создания/обновления Task c валидацией.
# 2) Рассчитать очки при approve и добавить в баланс ребёнка.
# 3) Все операции — транзакционные.
# 4) Логирование через loguru на уровне info/warning/error.
```

---

## 3) Докстринг-формат, который Copilot понимает

```python
def create_task(data: "TaskCreate") -> "Task":
    """
    Создать задание для ребёнка.

    Args:
        data: Валидационная схема с полями title, description, type, points, due_at, child_id, parent_id.
    Returns:
        Task: сохранённая модель SQLAlchemy.
    Raises:
        ValueError: если type не в {text, photo, video} или points < 1.
    Side effects:
        Пишет лог на уровне INFO, инициирует событие task.created.
    """
```

---

## 4) TODO-стиль (Copilot любит продолжать списки)

```python
# TODO: Валидировать дедлайн (due_at) > now()
# TODO: Ограничить points ∈ [1, 100]
# TODO: При approve — начислять очки и создавать запись в ledger
# TODO: Отправлять уведомление родителю в бот
```

---

## 5) Каркас моделей SQLAlchemy + pydantic-схем (минимум полей)

```python
# app/db/models.py
# Задача: определить минимальные модели для Task, CheckIn, Child, Parent, PointsLedger.
# Требования: явные типы, индексы, внешние ключи, soft-delete через is_active.

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum, Boolean, Text, func
import enum

class Base(DeclarativeBase):
    pass

class TaskType(str, enum.Enum):
    text = "text"
    photo = "photo"
    video = "video"

class TaskStatus(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    done = "done"
    approved = "approved"
    rejected = "rejected"

class Parent(Base):
    __tablename__ = "parents"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(index=True, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Child(Base):
    __tablename__ = "children"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    points: Mapped[int] = mapped_column(Integer, default=0)

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id", ondelete="CASCADE"), index=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    type: Mapped[TaskType] = mapped_column(Enum(TaskType))
    points: Mapped[int] = mapped_column(Integer, default=5)
    due_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.new)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

class CheckIn(Base):
    __tablename__ = "checkins"
    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), index=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    note: Mapped[str | None] = mapped_column(String(280))
    media_id: Mapped[str | None] = mapped_column(String(128))  # file_id из TG
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
```

```python
# app/api/schemas.py — pydantic
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str
    type: Literal["text", "photo", "video"]
    points: int = Field(ge=1, le=100, default=5)
    due_at: datetime | None = None
    child_id: int
    parent_id: int
```

---

## 6) Use-case промт: начисление очков (domain service)

```python
# Purpose: Сервис для approve задачи и начисления очков ребёнку.
# Requirements:
# - Вызов: approve_task(task_id:int, approved_by:int) -> Task
# - Меняет status → approved, добавляет child.points += task.points, пишет запись в ledger
# - Все в одной транзакции; если хоть что-то падает — rollback
# - Логирование: info при успехе, error при исключении
```

---

## 7) aiogram 3.x — хендлеры родителя/ребёнка

```python
# app/bot/handlers/parent_tasks.py
# Цель: Хендлеры для создания и модерации задач (Parent).
# Команды/кнопки:
# - "/task_new" — диалог FSM: заголовок → описание → тип → очки → дедлайн → подтверждение
# - "Мои задачи" — список с пэйджингом и кнопками Approve/Reject у выполненных
# Требования: короткие функции, FSMContext, фильтры на роль
```

```python
# app/bot/handlers/child_tasks.py
# Цель: Хендлеры для выполнения задач (Child).
# Команды/кнопки:
# - "Мои задания" — вывод активных; кнопки "Сдать" → запросить текст/фото/видео
# - При сдаче — сохранить media_id, статус → done, уведомить родителя
```

---

## 8) Шаблон healthcheck и конфигов

```python
# app/api/main.py
# Требования: GET /healthz -> {"status":"ok"}, /version -> git sha/env
# Загрузить конфиг из env: DATABASE_URL, BOT_TOKEN, ADMIN_IDS, LOG_LEVEL
```

---

## 9) Тест-первыми (pytest) — Copilot ориентируется на сигнатуры

```python
# tests/test_points.py
# Задача: протестировать approve_task.

def test_approve_task_adds_points(session, child_factory, task_factory):
    child = child_factory(points=0)
    task = task_factory(child_id=child.id, points=7, status="done")
    approve_task(task.id, approved_by=1)
    session.refresh(child)
    assert child.points == 7
```

---

## 10) Логи и ошибки (подсказка для Copilot)

```python
# Logging & Errors — правила:
# - log.info на бизнес-события (task.created, task.approved)
# - log.warning на странные, но допустимые кейсы
# - raise DomainError(code:str, message:str) для контролируемых ошибок
```

---

## 11) Планировщики и напоминания (cron/background)

```python
# Purpose: Ежедневные напоминания.
# Требования:
# - Фоновая задача каждые N минут: искать просроченные Task со статусом new/in_progress
# - Отправлять родителю digest и ребёнку gentle-reminder
```

---

## 12) Готовые промты для генерации UI-текста (RU)

```md
Сгенерируй лаконичные тексты кнопок Telegram-бота для семейного трекера привычек:
- Главный экран (родитель): "Создать задание", "Мои задания", "Уведомления", "Профиль"
- Экран задания (родитель): "Одобрить", "Отклонить", "Изменить", "Удалить"
- Главный экран (ребёнок): "Мои задания", "Сдать работу", "Мои очки"
Тон: дружелюбный, короткие фразы, без канцелярита.
```

---

## 13) Анти-паттерны (чтобы Copilot не уводило в сторону)

```md
Не делай:
- Монолитную функцию > 80 строк
- Запросы к БД внутри хендлеров бота — только через слой services
- Блокирующие операции в обработчиках (скачивание больших файлов) — выноси в background
```

---

## 14) Мини-«Definition of Done» для каждого PR

```md
- [ ] Есть тесты на доменную функцию
- [ ] Логи бизнес-событий добавлены
- [ ] Типы/схемы валидны, mypy проходит
- [ ] Хэндлеры короткие, без дублей
```

---

## 15) Пример полного промта в начале модуля сервиса

```python
# Purpose: Реализовать сервис TaskService с методами create, submit, approve, reject.
# Context: см. модели в app/db/models.py и схемы в app/api/schemas.py.
# Requirements:
# - методы атомарные, используют сессию SQLAlchemy через зависимость get_session
# - submit(task_id, child_id, payload) валидирует тип и сохраняет media/text
# - approve(task_id, parent_id) меняет статус и начисляет очки
# - reject(task_id, parent_id, reason) меняет статус, создаёт запись об отказе
# - логировать и возвращать pydantic DTO
```

---

# 16) North Star & Scope (для Copilot и команды)

**Цель продукта:** MiniApp Family Habit — родитель задаёт или выбирает задание → ребёнок видит в личном кабинете → выполняет (текст/фото/видео) → родитель проверяет → начисляются очки/монетки → ребёнок тратит в магазине на внутриигровые вещи → достижение порогов = награды от родителей.

**Ограничения MVP:** 1 родитель ↔ N детей, одна семья; магазин без реальных платежей (виртуальные монеты). Напоминания простые (ежедневный дайджест), без рекомендаций ИИ в MVP.

---

## 17) Архитектура (порядок и зависимости)

1. **DB слой (SQLAlchemy + Alembic)** → 2. **Domain services** → 3. **API (FastAPI)** → 4. **Bot (aiogram) & MiniApp (WebApp)** → 5. **Background jobs** → 6. **Shop/Rewards**.

Компоненты:

* **Postgres**: entities (Parent, Child, Task, CheckIn, PointsLedger, ShopItem, Purchase, RewardRule, Inventory).
* **FastAPI**: REST JSON для MiniApp + webhooks для бота.
* **Telegram Bot (aiogram 3)**: аутентификация, уведомления, FSM диалоги.
* **Telegram MiniApp (WebApp)**: React/TS фронт (SPA) внутри Telegram, общается с FastAPI.
* **Worker/CRON**: напоминания, зачистка просроченных, агрегаты очков.

Зависимости по слоям: UI → API DTO → Domain Services → Repos → DB.

---

## 18) Порядок сборки (итерации)

**M0 — Скелет и миграции**

1. База и модели (из п.5) + Alembic миграции.
2. Domain: TaskService, PointsService, ShopService (интерфейсы + пустые реализации).
3. FastAPI: /healthz, /version.

**M1 — Основной поток задач**
4) Endpoints: /auth/me, /children, /tasks (CRUD), /checkins (submit), /points/balance.
5) Bot: /start, роль Parent/Child, «Создать задание», «Мои задания».
6) Tests: unit на TaskService + e2e на /tasks.

**M2 — Начисления и магазин**
7) Approve/Reject + PointsLedger + баланс монет.
8) Shop: /shop/items (листинг), /shop/purchase (покупка), /inventory (список вещей).
9) MiniApp: экраны «Мои задания», «Сдать», «Мои монеты», «Магазин».

**M3 — Награды и напоминания**
10) RewardRule: пороги → события награды.
11) CRON: ежедневные напоминания родителю/ребёнку.
12) Админ-минимум: добавление ShopItem, RewardRule через API.

---

## 19) Модель данных (минимум для MVP)

* **Parent(id, tg_id, is_active)**
* **Child(id, parent_id, name, points, coins)**
* **Task(id, parent_id, child_id, title, description, type, points, coins, due_at, status)**
* **CheckIn(id, task_id, child_id, note, media_id, created_at)**
* **PointsLedger(id, child_id, delta_points, delta_coins, reason, ref_id, created_at)**
* **ShopItem(id, sku, title, description, price_coins, is_active)**
* **Purchase(id, child_id, item_id, cost_coins, created_at)**
* **RewardRule(id, title, threshold_points, reward_type, payload)**
* **Inventory(id, child_id, item_id, qty, meta)**

Правила:

* `Task.points` и `Task.coins` могут отличаться (очки — прогресс, монеты — валюта магазина).
* Ledger — единственный источник правды по изменениям.

---

## 20) Бизнес-потоки (упорядоченно)

**A. Создание и выполнение задачи**

1. Parent создаёт Task → status=new.
2. Child открывает MiniApp → «Мои задания» (new/in_progress)
3. Child сдаёт работу (submit) → создаётся CheckIn → Task.status=done.
4. Parent approves → Task.status=approved → начислить points/coins → запись в Ledger.

**B. Покупка в магазине**

1. Child открывает «Магазин» → листинг ShopItem.
2. Выбирает товар → POST /shop/purchase.
3. Проверка баланса → списание coins → запись в Purchase + Ledger → добавление в Inventory.

**C. Награды**

1. Каждое approve проверяет RewardRule (threshold_points).
2. Если достигнуто — создать событие reward.triggered → уведомить Parent/Child.

---

## 21) Машины состояний (FSM)

**Task.status**: `new → in_progress → done → approved | rejected`

* `in_progress` ставится при первом открытии задания ребёнком или явном «Начать».
* `done` — при отправке CheckIn.
* `approved/rejected` — решает Parent.

**Purchase.status** (на будущее): `pending → confirmed → delivered` (в MVP — сразу confirmed).

---

## 22) Контракты API (минимум)

```
GET  /auth/me                 → { role: "parent"|"child", user_id, family_id }
GET  /children                → [Child]
POST /tasks                   → Task
GET  /tasks?child_id=&status= → [Task]
POST /checkins                → CheckIn  (task_id, payload)
POST /tasks/{id}/approve      → Task + ledger deltas
POST /tasks/{id}/reject       → Task
GET  /points/balance?child_id → { points, coins }
GET  /shop/items              → [ShopItem]
POST /shop/purchase           → Purchase + { new_balance }
GET  /inventory               → [Inventory]
```

Требования: pydantic DTO, 400 на валидации, 403 на доступе не к своему ребёнку, идемпотентность через `Idempotency-Key` заголовок (MVP опционально).

---

## 23) MiniApp (WebApp) — экраны и порядок

**Parent**

* Главная: «Создать задание», «Мои задания», «Награды», «Профиль семьи»
* Создание задачи: пошаговая форма (title → description → type → points/coins → due_at → child)
* Модерация: список "done" с карточками → Approve/Reject

**Child**

* Главная: «Мои задания», «Сдать работу», «Мои монеты», «Магазин»
* Задания: фильтр по статусу, карточка → «Начать»/«Сдать»
* Сдача: ввод текста или загрузка фото/видео (file_id), комментарий
* Магазин: карточки товара → «Купить» → диалог подтверждения → результат + новый баланс

---

## 24) Copilot: «Праймер структуры» (вставлять в начало файлов)

```python
# Structure Primer for Copilot
# 1) Этот модуль НЕ ходит в Telegram, только доменная логика.
# 2) Все побочные эффекты (БД, события) — через интерфейсы/репозитории.
# 3) Функции короткие, явные типы. Исключения — DomainError.
# 4) На каждый публичный метод есть тест в tests/.
```

---

## 25) Очерёдность коммитов (чтобы Copilot «держал линию»)

1. feat(db): базовые модели + миграции
2. feat(domain): TaskService.create/submit/approve + интерфейсы Repo
3. feat(api): /tasks, /checkins, /points — DTO и роуты
4. feat(bot): /start, роли, «Создать задание», «Мои задания»
5. feat(webapp): экраны Child (список/сдача/баланс), Parent (модерация)
6. feat(shop): items, purchase, inventory, ledger
7. feat(rewards): rules + триггеры
8. chore(cron): daily reminders
9. test(e2e): happy-path сценарии

---

## 26) Тест-планы (минимум кейсов)

* Task.create: валидация type/points/due_at
* Submit: запрет не совпадающего типа (например, text при требуемом photo)
* Approve: начисление points/coins, запись в Ledger, единожды
* Purchase: недостаточно монет → 400; успех → уменьшение баланса, Inventory++
* RewardRule: достижение порога → событие

---

## 27) Готовые промты для Copilot по шагам

**A. Реализация Ledger**

```python
# Purpose: Реализовать PointsLedgerRepo с методами add_delta(child_id, delta_points, delta_coins, reason, ref_id)
# Requirements: одна транзакция; возвращать новый баланс; логировать операции
```

**B. Approve Task**

```python
# Purpose: В TaskService.approve начислить очки/монеты, записать Ledger, вернуть DTO
# Requirements: идемпотентность — повторный approve ничего не меняет
```

**C. Покупка товара**

```python
# Purpose: ShopService.purchase(child_id, item_id)
# Requirements: проверить баланс, списать coins, записать Purchase и Ledger, выдать Inventory
```

**D. WebApp экран «Мои задания»**

```tsx
// Purpose: Список задач ребёнка с фильтрами и экшнами «Начать»/«Сдать»
// Requirements: fetch /tasks?child_id=&status=, debounce, optimistic UI на submit
```

---

## 28) Definition of Ready (до того как просить Copilot писать код)

* Сформулирован точный контракт функции/эндпоинта
* Пример входных/выходных данных
* Описаны ошибки и idempotency
* Написан тест-шаблон (пусть даже pending)

---

## 29) Мини-гайд по ролям и доступам

* Parent видит/меняет только своих детей/задачи
* Child видит только себя
* Все мутации проверяют владельца по `parent_id`
* Логи: кто инициировал действие (tg_id, user_id)

---

## 30) Что дальше

Готов расширить Cookbook под твой стек фронта (React/TS для MiniApp) и добавить шаблон проекта с готовыми файлами: `render.yaml`, `.env.example`, `docker-compose.yml`, базовые роуты FastAPI и каркас aiogram.

---

# 31) 🚀 End-to-End Quickstart: Telegram MiniApp + GitHub + Test

Ниже — самый короткий рабочий путь: MiniApp (React/TS) на GitHub Pages + Backend (FastAPI) на Render + Telegram Bot (aiogram) как шлюз.

## A) Создание бота у BotFather (1 раз)

1. В Telegram → @BotFather → `/newbot` → придумай имя + юзернейм → получи **BOT_TOKEN**.
2. Включи веб-приложение: `/setmenubutton` → выбери бота → **Choose a chat**: Default → **Type**: Web App → **Text**: `Family Habit` → **Web App URL**: `https://<твоя-GitHub-Pages-страница>` (добавим позже).
3. Ограничь доступ: `/setdomain` → укажи домен бэкенда (например, `family-habit.onrender.com`).

> Примечание: кнопку WebApp можно также показать внутри инлайн-кнопок в чате — см. раздел **D**.

---

## B) GitHub: фронтенд MiniApp (React/TS + Telegram WebApp SDK)

**1. Репозиторий**: `family-habit-miniapp`

**2. Файлы** (минимальный скелет)

```
/ (root)
  package.json
  vite.config.ts
  index.html
  src/
    main.tsx
    App.tsx
    api.ts
    tg.d.ts
```

**3. package.json**

```json
{
  "name": "family-habit-miniapp",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.7.7",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "typescript": "^5.6.2",
    "vite": "^5.4.8",
    "@types/react": "^18.3.5",
    "@types/react-dom": "^18.3.0"
  }
}
```

**4. vite.config.ts**

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/family-habit-miniapp/', // если включишь GitHub Pages для репо с таким именем
})
```

**5. index.html**

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Family Habit</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**6. src/tg.d.ts** — чтобы TS знал про Telegram SDK

```ts
export {};
declare global {
  interface Window { Telegram: any }
}
```

**7. src/api.ts** — простая обёртка

```ts
import axios from 'axios'
const API_BASE = import.meta.env.VITE_API_BASE

export const api = axios.create({ baseURL: API_BASE })

export function authHeaders() {
  // Для бэка можно валидировать initData. В MVP передаём tg_initData_raw как есть
  const tg = window.Telegram?.WebApp
  return tg ? { 'X-TG-Init-Data': tg.initData || '' } : {}
}
```

**8. src/main.tsx**

```ts
import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

createRoot(document.getElementById('root')!).render(<App />)
```

**9. src/App.tsx** — 3 экрана: «Мои задания», «Сдать», «Магазин»

```tsx
import React, { useEffect, useState } from 'react'
import { api, authHeaders } from './api'

type Task = { id:number; title:string; status:string; type:'text'|'photo'|'video' }

enum Tab { Tasks='tasks', Submit='submit', Shop='shop' }

export default function App(){
  const tg = (window as any).Telegram?.WebApp
  const [tab, setTab] = useState<Tab>(Tab.Tasks)
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(()=>{ tg?.expand(); tg?.ready(); },[])
  useEffect(()=>{ fetchTasks() },[])

  async function fetchTasks(){
    try {
      setLoading(true)
      const { data } = await api.get('/tasks', { headers: authHeaders() })
      setTasks(data)
    } finally { setLoading(false) }
  }

  async function approveDemo(taskId:number){
    await api.post(`/tasks/${taskId}/approve`, {}, { headers: authHeaders() })
    await fetchTasks()
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>Family Habit</h2>
      <nav style={{ display:'flex', gap:8, marginBottom:12 }}>
        <button onClick={()=>setTab(Tab.Tasks)}>Мои задания</button>
        <button onClick={()=>setTab(Tab.Submit)}>Сдать</button>
        <button onClick={()=>setTab(Tab.Shop)}>Магазин</button>
      </nav>

      {tab===Tab.Tasks && (
        <section>
          {loading ? 'Загрузка…' : tasks.map(t=> (
            <div key={t.id} style={{ border:'1px solid #ccc', borderRadius:8, padding:12, marginBottom:8 }}>
              <div><b>{t.title}</b></div>
              <div>Статус: {t.status}</div>
              <div>Тип: {t.type}</div>
              <div style={{ marginTop:8 }}>
                <button onClick={()=>approveDemo(t.id)}>✓ Быстрый approve (демо)</button>
              </div>
            </div>
          ))}
        </section>
      )}

      {tab===Tab.Submit && (
        <section>
          <p>В MVP отправка сделает POST /checkins (заглушка)</p>
        </section>
      )}

      {tab===Tab.Shop && (
        <section>
          <p>Магазин подключим на шаге M2</p>
        </section>
      )}
    </div>
  )
}
```

**10. GitHub Pages**

* Settings → Pages → Build from `GitHub Actions`.
* Добавь workflow `.github/workflows/pages.yml`:

```yaml
name: Deploy Pages
on: { push: { branches: [ main ] } }
permissions: { contents: read, pages: write, id-token: write }
jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-pages-artifact@v3
        with: { path: dist }
      - uses: actions/deploy-pages@v4
```

* После деплоя получишь URL вида: `https://<user>.github.io/family-habit-miniapp/` → этот URL вставь в BotFather как **Web App URL**.

---

## C) Бэкенд: FastAPI + Render (минимум)

**1. Репозиторий**: `family-habit-backend`

**2. Файлы**

```
/ (root)
  app.py
  requirements.txt
  render.yaml
```

**3. requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
python-multipart==0.0.9
```

**4. app.py** — заглушки для теста MiniApp

```python
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], allow_credentials=True,
    allow_methods=['*'], allow_headers=['*'],
)

# Простейшие данные для демонстрации
TASKS = [
    {"id": 1, "title": "Убрать комнату", "status": "new", "type": "photo"},
    {"id": 2, "title": "Прочитать 10 стр.", "status": "done", "type": "text"},
]

@app.get('/healthz')
def healthz():
    return {"status":"ok"}

@app.get('/tasks')
def list_tasks(x_tg_init_data: str | None = Header(default=None, convert_underscores=False)):
    # В MVP пропускаем валидацию initData; в проде — проверь подпись HMAC
    return TASKS

@app.post('/tasks/{task_id}/approve')
def approve_task(task_id: int, x_tg_init_data: str | None = Header(default=None, convert_underscores=False)):
    for t in TASKS:
        if t["id"] == task_id:
            t["status"] = "approved"
            return {"ok": True, "task": t}
    return {"ok": False, "error": "not_found"}
```

**5. render.yaml** — автодеплой на Render

```yaml
services:
  - type: web
    name: family-habit-api
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
    autoDeploy: true
```

**Деплой**: подключи репозиторий на render.com → New Web Service → автоконфиг возьмёт `render.yaml` → после билда получишь URL `https://family-habit-api.onrender.com` → добавь в MiniApp `.env` переменную `VITE_API_BASE`.

В Vite локально: создай `.env` в корне фронта:

```
VITE_API_BASE=https://family-habit-api.onrender.com
```

---

## D) Инлайн-кнопка для запуска MiniApp из чата (aiogram 3)

**Зачем:** пользователю удобно открыть MiniApp нажатием кнопки.

Минимальный бот (можно в отдельном проекте):

```python
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL')  # URL GitHub Pages

async def main():
    dp = Dispatcher()
    bot = Bot(BOT_TOKEN)

    @dp.message()
    async def start(m: types.Message):
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Открыть Family Habit', web_app=WebAppInfo(url=WEBAPP_URL))]])
        await m.answer('Запускаем мини-приложение:', reply_markup=kb)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
```

Запуск локально: `BOT_TOKEN=123 WEBAPP_URL=https://<user>.github.io/family-habit-miniapp/ python bot.py`

---

## E) Чек-лист теста (10 минут)

* [ ] GitHub Pages выдал публичный URL MiniApp
* [ ] Render API отвечает `GET /healthz → {status: ok}`
* [ ] В MiniApp в консоли нет CORS-ошибок (иначе проверь `allow_origins`)
* [ ] В MiniApp список задач грузится (GET /tasks)
* [ ] Кнопка «✓ Быстрый approve (демо)» меняет статус карточки
* [ ] В Telegram: из чата с ботом кнопка «Открыть Family Habit» запускает MiniApp без ошибок

---

## F) Типичные ошибки и быстрое лечение

* **CORS / Mixed Content**: используй HTTPS везде, на Render уже есть.
* **GitHub Pages 404**: проверь `base` в `vite.config.ts` и включённый Pages workflow.
* **BotFather Web App URL не открывается**: вставь точный URL GitHub Pages; убедись, что страница публична.
* **InitData проверка**: для MVP отключена; для продакшна реализуй HMAC-валидацию согласно `tg.initData` (позже добавим в бэк).
* **Render «cold start»**: первый запрос может быть дольше — дождись ответа и проверь логи.

---

## G) Следующие шаги (за пределами демо)

* Реальная БД (Postgres) + SQLAlchemy, Alembic миграции
* Auth на основе `initData` + привязка Parent/Child
* Экраны: «Сдать работу» (POST /checkins) с загрузкой `file_id`
* Магазин и монеты (M2) + RewardRule (M3)

Готов расширить этот раздел полноценным шаблоном репо (frontend+backend) и добавить GitHub Actions под бэкенд (Docker или Render Deploy Hook), а также скрипт инициализации БД.

---

# 32) Тарифы и ограничения (free vs pro)

**Free (по умолчанию):**

* 1 ребёнок на семью
* максимум 5 активных заданий (по всем статусам, кроме approved/rejected) одновременно
* 5 медалей/нагород (видимых в профиле)
* 3 аватарки на выбор для девочки и 3 — для мальчика
* статистика урезана: только счётчик выполненных задач за 7 дней и общий баланс очков/монет

**Pro (299 ₽/мес):**

* дети: 1 → N (по умолчанию 5, конфигурируемо)
* задания: без лимита (или большой лимит, например 200)
* расширенные аватары (10+ на пол), питомцы, одежда (скины), магазин внутриигровых предметов
* полноценная статистика: дневная/недельная/месячная, топ-навыки, heatmap
* геймификация: питомцы с уровнем, ежедневные серии (streaks), квесты

> Цена подписки: **299 ₽/мес** (env: `SUB_PRICE_RUB=299`).

---

## 33) Фича-флаги и правила проверки (для Copilot и кода)

Вводим enum тарифа и централизованные гварды-валидаторы.

```python
# app/core/plan.py
from enum import Enum

class Plan(str, Enum):
    FREE = "free"
    PRO = "pro"

FREE_LIMITS = {
    "max_children": 1,
    "max_active_tasks": 5,  # new/in_progress/done суммарно
    "max_medals": 5,
    "avatars_per_gender": 3,
    "stats_scope": "basic",  # {basic, full}
}

PRO_LIMITS = {
    "max_children": 5,       # можно поднять через конфиг/параметр
    "max_active_tasks": 200,
    "max_medals": 999,
    "avatars_per_gender": 99,
    "stats_scope": "full",
}

def limits_for(plan: Plan) -> dict:
    return FREE_LIMITS if plan == Plan.FREE else PRO_LIMITS
```

### Сервис проверки лимитов

```python
# app/services/limits.py
from app.core.plan import Plan, limits_for
from app.db import repo

class LimitError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code

async def ensure_can_add_child(family_id: int, plan: Plan):
    limits = limits_for(plan)
    count = await repo.children_count(family_id)
    if count >= limits["max_children"]:
        raise LimitError("limit_children", "Лимит детей в бесплатной версии")

async def ensure_can_create_task(family_id: int, plan: Plan):
    limits = limits_for(plan)
    active = await repo.tasks_active_count(family_id)
    if active >= limits["max_active_tasks"]:
        raise LimitError("limit_tasks", "Достигнут лимит активных заданий в бесплатной версии")
```

### Использование гвардов в сервисах

```python
# TaskService.create(...)
# 1) определить план семьи (из Family.plan)
# 2) вызвать ensure_can_create_task(...)
# 3) продолжить сохранение
```

---

## 34) Модель Family и хранение плана

Добавляем сущность **Family** и поле плана.

```python
# app/db/models.py (фрагмент)
class Family(Base):
    __tablename__ = "families"
    id: Mapped[int] = mapped_column(primary_key=True)
    plan: Mapped[str] = mapped_column(String(8), default="free", index=True)  # free|pro

class Parent(Base):
    __tablename__ = "parents"
    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id", ondelete="CASCADE"), index=True)
    tg_id: Mapped[int] = mapped_column(index=True, unique=True)
```

---

## 35) API: ответы при превышении лимитов

```python
# Пример FastAPI handler
from fastapi import HTTPException

try:
    await ensure_can_create_task(family_id, plan)
except LimitError as e:
    raise HTTPException(status_code=402, detail={
        "code": e.code,
        "message": "Доступно в Pro-версии. Оформите подписку за 299 ₽/мес.",
        "price_rub": 299,
        "upgrade_hint": True
    })
```

> Используем **402** (Payment Required) как явный сигнал фронту показать экран апгрейда (или 409 с отдельным кодом, если 402 нежелателен).

---

## 36) MiniApp: UX-блокировка и апселл

**Правила в UI:**

* Если `plan=free`, в Child-профиле показывать «3/3 аватаров», остальные — с замком.
* Кнопки «Добавить ребёнка», «Создать задание» после 5 активных — ведут на апгрейд-модалку.
* Статистика: отображать только счётчики «за 7 дней» и «всего». Графики/heatmap — скрыты с подсказкой «Доступно в Pro».

**Компонент UpgradeModal (тексты RU):**

```
Заголовок: Больше свободы с Family Habit Pro
Пулиты:
• До 5 детей и без лимитов на задания
• Полная статистика и прогресс-heatmap
• Аватары, питомцы, одежда и магазин
Кнопка: Перейти на Pro — 299 ₽/мес
Ссылка: Подробнее о подписке
```

---

## 37) Подписка (MVP-заглушка)

Пока без платёжного провайдера — делаем заглушку эндпойнта:

```
POST /billing/subscribe → { status:"ok", plan:"pro", next_billing:"2025-11-03" }
```

В БД: `Family.plan = 'pro'`.

> Позже подключим реальный биллинг (ЮKassa/Robokassa) и вебхуки. Цена берётся из env `SUB_PRICE_RUB`.

---

## 38) Статистика: базовая vs полная

**basic (free):** `GET /stats/basic?child_id=` → `{ done_7d:int, total_points:int, total_coins:int }`

**full (pro):** `GET /stats/full?child_id=` → `{ daily:[...], weekly:[...], skills:[...], heatmap:[...], streak:int }`

Фронт должен вызывать только доступный для плана метод.

---

## 39) Аватары и каталог

* Каталог аватаров разделён по полу и помечается флагом `pro_only: bool`.
* Для free отдаём первые 3 варианта на пол; остальные — скрыты или приходят, но с `locked=true`.

```ts
// /avatars?gender=female
[
  { id: 'f1', url: '...', locked: false },
  { id: 'f2', url: '...', locked: false },
  { id: 'f3', url: '...', locked: false },
  { id: 'f4', url: '...', locked: true,  pro_only: true },
]
```

---

## 40) Тест-кейсы на лимиты

* **children_limit_free**: при 1 ребёнке попытка добавить второго → 402 + код `limit_children`.
* **tasks_limit_free**: на 5-м активном всё ок, на 6-м → 402 + `limit_tasks`.
* **avatars_free**: выдаётся ровно 3 аватарки на пол, остальные `locked`.
* **stats_free**: обращение к /stats/full на free → 403.
* **upgrade_flow**: после /billing/subscribe план меняется на pro, повторная операция проходит.

---

## 41) UI-строки (RU) для апселла

* «В бесплатной версии доступен 1 ребёнок и 5 заданий. Разблокируй полный потенциал за 299 ₽/мес.»
* «Ещё один ребёнок? Подключи Pro — до 5 детей на семью.»
* «Расширенные аватарки, питомцы и гардероб — только в Pro.»
* «Полная статистика прогресса и heatmap — доступно в Pro.»
