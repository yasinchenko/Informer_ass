# file: bot/main.py
import os
import logging
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import requests
import re
from datetime import datetime, timedelta

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000/log")
ANALYZE_API = os.getenv("ANALYZE_API", "http://localhost:8000/analyze")

logging.basicConfig(level=logging.INFO)

# Helper to request analysis from API and reply
async def _request_analyze(message, date_from_dt: datetime, date_to_dt: datetime) -> None:
    date_from = date_from_dt.strftime("%Y-%m-%d")
    date_to = date_to_dt.strftime("%Y-%m-%d")
    params = {
        "chat_id": message.chat_id,
        "from": date_from,
        "to": date_to,
    }

    try:
        response = requests.get(ANALYZE_API, params=params)
        if response.status_code == 400:
            detail = response.json().get("detail", "Некорректный запрос")
            await message.reply_text(detail)
            return
        if response.status_code != 200:
            raise Exception(response.text)

        result = response.json()
        top_words = result.get("top_words", [])
        summary = result.get("summary", "")

        words_block = "\n".join(
            [f"{i+1}. {w['word']} — {w['count']}" for i, w in enumerate(top_words)]
        )
        reply = (
            f"Анализ за период {date_from_dt.strftime('%d.%m.%Y')} - "
            f"{date_to_dt.strftime('%d.%m.%Y')}:\n\nТоп-5 слов:\n{words_block}"\
            f"\n\nТемы обсуждений:\n{summary}"
        )
        await message.reply_text(reply)
    except Exception as e:
        logging.error(f"Analyze error: {e}")
        await message.reply_text("Ошибка при получении анализа. Попробуйте позже.")

# Обработка входящих текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message and message.text:
        data = {
            "chat_id": message.chat_id,
            "message_id": message.message_id,
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "text": message.text,
            "timestamp": message.date.isoformat()
        }
        try:
            requests.post(API_URL, json=data)
        except Exception as e:
            logging.error(f"Failed to send log to API: {e}")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    await message.reply_text("Бот активен и готов к логированию сообщений.")

# Команда /analyze с <дата> по <дата>
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    text = message.text
    match = re.search(r"/analyze\s+с\s+(\d{2}\.\d{2}\.\d{4})\s+по\s+(\d{2}\.\d{2}\.\d{4})", text)
    if not match:
        await message.reply_text("Формат команды: /analyze с 01.06.2025 по 05.06.2025")
        return

    try:
        date_from_dt = datetime.strptime(match.group(1), "%d.%m.%Y")
        date_to_dt = datetime.strptime(match.group(2), "%d.%m.%Y")
    except ValueError:
        await message.reply_text("Неверный формат даты. Используйте ДД.ММ.ГГГГ")
        return

    delta_days = (date_to_dt - date_from_dt).days + 1
    logging.info(
        f"Parsed dates: from {date_from_dt}, to {date_to_dt}, delta {delta_days}"
    )
    if delta_days > 30:
        await message.reply_text(
            "Период анализа должен быть не более 30 дней. "
            "Укажите даты в пределах 30 дней."
        )
        return

    await _request_analyze(message, date_from_dt, date_to_dt)


async def _analyze_last(update: Update, context: ContextTypes.DEFAULT_TYPE, days: int):
    message = update.effective_message
    date_to_dt = datetime.utcnow()
    date_from_dt = date_to_dt - timedelta(days=days - 1)
    await _request_analyze(message, date_from_dt, date_to_dt)


async def analyze7(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("/analyze7 command received")
    await _analyze_last(update, context, 7)


async def analyze14(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("/analyze14 command received")
    await _analyze_last(update, context, 14)


async def analyze30(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("/analyze30 command received")
    await _analyze_last(update, context, 30)

async def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    await app.bot.set_my_commands(
        [
            BotCommand("start", "Запуск бота"),
            BotCommand("analyze", "Анализ по датам"),
            BotCommand("analyze7", "Последние 7 дней"),
            BotCommand("analyze14", "Последние 14 дней"),
            BotCommand("analyze30", "Последние 30 дней"),
        ]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("analyze7", analyze7))
    app.add_handler(CommandHandler("analyze14", analyze14))
    app.add_handler(CommandHandler("analyze30", analyze30))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started...")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
