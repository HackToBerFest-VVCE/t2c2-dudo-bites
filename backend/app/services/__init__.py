from __future__ import annotations

import re
from typing import Iterable


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_account_id(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()
