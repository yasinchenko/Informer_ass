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

    prompt = f"Кратко подытожь следующий текст:\n{text}"
    payload = {"callback_url": None, "messages": [{"role": "user", "content": prompt}]}

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
                data.get("summary")
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


def summarize_text(text: str, max_sentences: int = 3) -> str:
    """
    Возвращает краткое резюме текста на основе первых информативных предложений.
    Если текст слишком короткий — возвращает его как есть.

    :param text: исходный текст
    :param max_sentences: максимальное число предложений в резюме
    :return: строка с кратким описанием
    """
    api_summary = _fetch_summary_from_api(text)
    if api_summary:
        return api_summary

    # Простейшее разбиение по предложениям
    sentences = text.replace("!", ".").replace("?", ".").split(".")
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not sentences:
        return "Заглушка: темы обсуждений будут здесь"

    summary = ". ".join(sentences[:max_sentences])
    return summary + "." if not summary.endswith(".") else summary
