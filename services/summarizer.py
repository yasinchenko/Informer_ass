# file: services/summarizer.py

import os
import logging
from typing import Optional

import httpx

# Endpoint агрегатора нейросетей. Используем сеть DeepSeek для генерации
# саммари.
GEN_API_URL = "https://api.gen-api.ru/api/v1/networks/deepseek-v3"


def _fetch_summary_from_api(text: str) -> Optional[str]:
    """Возвращает саммари с https://api.gen-api.ru или ``None`` при ошибке."""
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        return None

    prompt = (
        f"Кратко выдели пунктами темы, которые обсуждались в тексте:\n{text}"
    )
    payload = {
        "callback_url": None,
        "is_sync": True,
        "messages": [{"role": "user", "content": prompt}],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = httpx.post(GEN_API_URL, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            summary = (
                data.get("output")
                or data.get("summary")
                or data.get("result")
                or data.get("text")
            )
            if not summary:
                # Формат ответа в стиле OpenAI
                choices = data.get("choices")
                if choices and isinstance(choices, list):
                    msg = choices[0].get("message") if choices else None
                    if msg and isinstance(msg, dict):
                        summary = msg.get("content")
            if summary:
                return str(summary).strip()
        elif isinstance(data, str):
            return data.strip()
    except Exception as exc:
        logging.error("Failed to fetch summary from API: %s", exc)
    return None


def summarize_text(text: str) -> str:
    """Возвращает краткое резюме текста через GenAPI.

    Если ключ API не указан или запрос завершился ошибкой,
    возвращает уведомление о недоступности саммари.
    """

    api_summary = _fetch_summary_from_api(text)
    if api_summary:
        return api_summary

    return "Саммари недоступно"

