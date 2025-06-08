# file: services/analyzer.py
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from typing import List


nltk.download("stopwords", quiet=True)

stop_words = set(stopwords.words("russian") + stopwords.words("english"))


def analyze_texts(texts: List[str]) -> tuple[list[dict], str]:
    all_text = " ".join(texts).lower()
    words = re.findall(r"\b\w{3,}\b", all_text)
    filtered = [w for w in words if w not in stop_words]
    freq = Counter(filtered).most_common(5)
    top_words = [{"word": w, "count": c} for w, c in freq]
    summary = summarize_text(all_text)
    return top_words, summary
