# file: database/models.py
from pydantic import BaseModel

class LogMessage(BaseModel):
    chat_id: int
    message_id: int
    user_id: int
    username: str | None
    text: str
    timestamp: str
