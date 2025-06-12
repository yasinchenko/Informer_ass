# file: services/summarizer.py

import os
import logging
import time
from typing import Optional

import httpx

# Endpoint агрегатора нейросетей. Используем сеть DeepSeek для генерации
# саммари.
GEN_API_URL = "https://api.gen-api.ru/api/v1/networks/deepseek-v3"


def _extract_summary(data: dict) -> Optional[str]:
    """Извлекает текст саммари из ответа API."""
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
    return None


def _fetch_summary_from_api(text: str) -> Optional[str]:
    """Возвращает саммари с https://api.gen-api.ru или ``None`` при ошибке."""
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        return None

    prompt = (
        f"Кратко выдели пунктами темы, которые обсуждались в тексте:\n{text}"
    )
    payload = {
        
        "is_sync": True,
        "model": "deepseek-v3",
        "messages": [{"role": "user", "content": prompt}],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = httpx.post(
            GEN_API_URL, json=payload, headers=headers, timeout=20
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            if data.get("status") == "success":
                summary = _extract_summary(data)
                if summary:
                    return summary
            request_id = data.get("request_id")
            if request_id:
                poll_url = f"https://api.gen-api.ru/api/v1/request/get/{request_id}"
                for _ in range(5):
                    try:
                        resp = httpx.get(poll_url, headers=headers, timeout=20)
                        resp.raise_for_status()
                        result = resp.json()
                        if result.get("status") == "success":
                            summary = _extract_summary(result)
                            if summary:
                                return summary
                        elif result.get("status") == "failed":
                            break
                    except Exception as exc:
                        logging.error("Polling error: %s", exc)
                        break
                    time.sleep(1)
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

