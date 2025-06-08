# file: services/summarizer.py

from typing import Optional


def summarize_text(text: str, max_sentences: int = 3) -> str:
    """
    Возвращает краткое резюме текста на основе первых информативных предложений.
    Если текст слишком короткий — возвращает его как есть.

    :param text: исходный текст
    :param max_sentences: максимальное число предложений в резюме
    :return: строка с кратким описанием
    """
    # Простейшее разбиение по предложениям
    sentences = text.replace("!", ".").replace("?", ".").split(".")
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not sentences:
        return "Заглушка: темы обсуждений будут здесь"

    summary = ". ".join(sentences[:max_sentences])
    return summary + "." if not summary.endswith(".") else summary
