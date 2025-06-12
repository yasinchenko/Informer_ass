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
TELEGRAM_TOKEN=7953491746:AAEcULVXG_I1lgWdOXRqGCOdx5DMBI98hLE
AI_API_KEY=sk-WKwVSql3WXC02No86QuiL6mhtJwZgA07Qx3qYpTMkmLGSpuB97XpFiindSG5
DB_FILE=messages.db
```
Переменная `AI_API_KEY` необязательна. Если ключ не указан или запрос к API
завершается ошибкой, бот вернёт короткое резюме при помощи встроенной эвристики.
Бот обращается к агрегатору нейросетей по адресу
`https://api.gen-api.ru/api/v1/networks/deepseek-v3`.
Запрос отправляется в синхронном режиме с параметром `is_sync: true`, чтобы
получать результат сразу в ответе.

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
httpx
python-telegram-bot
python-dotenv
nltk
```

---

## 📌 Примечания

- Используется API https://api.gen-api.ru
- Для обращения к API нужен ключ `AI_API_KEY`
- Поддерживается только текст в групповых чатах
- Период анализа ограничен 7 днями, 4000 токенов

---

## 🛠️ Roadmap (будущее)

- PDF/инфографика отчёта
- Сравнение активности участников
- Ранжирование, геймификация
- Монетизация
