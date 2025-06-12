# file: services/summarizer.py

import os
import logging
from typing import Optional

import httpx

GEN_API_URL = "https://api.gen-api.ru/text/summarize"


def _fetch_summary_from_api(text: str) -> Optional[str]:
    """Возвращает саммари с https://api.gen-api.ru или ``None`` при ошибке."""
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        return None

    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = httpx.post(GEN_API_URL, json={"text": text}, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            # Ожидаем поле "summary" в ответе
            summary = data.get("summary") or data.get("result") or data.get("text")
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
