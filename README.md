# Informer_ass — Telegram Chat Analyzer Bot (MVP)

## 🚀 Назначение

Этот проект — MVP Telegram-бота, который анализирует сообщения в групповых чатах и:
- сохраняет их в базу данных;
- формирует частотный анализ;
- генерирует AI-саммари обсуждений.

---

## 🗂️ Структура проекта

```
informer_ass/
├── api/                # FastAPI сервер с endpoints
├── bot/                # Telegram-бот
├── database/           # Работа с SQLite: модели и CRUD
├── services/           # Частотный анализ и AI-саммари
├── .env                # Переменные окружения
├── requirements.txt    # Зависимости pip
└── README.md
```

---

## ⚙️ Установка

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Создай `.env` файл:
```env
TELEGRAM_TOKEN=<токен от BotFather>
AI_API_KEY=sk-...  # от gen-api.ru
DB_FILE=messages.db
```

---

## ▶️ Запуск

**1. FastAPI сервер:**
```bash
uvicorn api.main:app --reload
```

**2. Telegram-бот:**
```bash
python bot/main.py
```

---

## 🧪 Пример использования

В групповом чате:
```text
/analyze с 01.06.2025 по 05.06.2025
```
Бот ответит:
```
Анализ за период 01.06.2025 — 05.06.2025

Топ-5 слов:
1. проект — 42
2. бот — 38
...

Темы обсуждения:
— Разработка Telegram-бота
— AI-обработка текста
```

---

## 📦 Зависимости

```
fastapi
uvicorn
requests
python-telegram-bot
python-dotenv
nltk
```

---

## 📌 Примечания

- Используется API https://api.gen-api.ru
- Поддерживается только текст в групповых чатах
- Период анализа ограничен 7 днями, 4000 токенов

---

## 🛠️ Roadmap (будущее)

- PDF/инфографика отчёта
- Сравнение активности участников
- Ранжирование, геймификация
- Монетизация
