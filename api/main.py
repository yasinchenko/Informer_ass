# file: api/main.py
import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

from database import crud
from database.models import LogMessage
from services.analyzer import analyze_texts

# Логирование в файл
logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = os.getenv("DB_FILE", "messages.db")

@app.on_event("startup")
def startup():
    logging.info("Startup: Инициализация базы данных")
    crud.init_db(DB_FILE)

@app.post("/log")
def log_message(msg: LogMessage):
    try:
        crud.insert_message(DB_FILE, msg)
        logging.info(f"LOG: сообщение сохранено: chat_id={msg.chat_id} msg_id={msg.message_id}")
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Ошибка при логировании: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze")
def analyze(
    chat_id: int = Query(..., description="ID чата Telegram"),
    from_: str = Query(..., alias="from", description="Дата начала в формате YYYY-MM-DD"),
    to: str = Query(..., description="Дата окончания в формате YYYY-MM-DD")
):
    try:
        date_from = datetime.strptime(from_, "%Y-%m-%d")
        date_to = datetime.strptime(to, "%Y-%m-%d")
        if (date_to - date_from).days > 7:
            raise HTTPException(status_code=400, detail="Период анализа не должен превышать 7 дней")

        texts = crud.get_texts_by_chat_and_date(DB_FILE, chat_id, from_, to)
        logging.info(f"ANALYZE: chat_id={chat_id}, from={from_}, to={to}, messages={len(texts)}")
        top_words, summary = analyze_texts(texts)
        return {"top_words": top_words, "summary": summary}
    except ValueError:
        logging.warning("Неверный формат даты")
        raise HTTPException(status_code=400, detail="Неверный формат даты. Используй YYYY-MM-DD")
    except Exception as e:
        logging.error(f"Ошибка анализа: {e}")
        raise HTTPException(status_code=500, detail=str(e))
