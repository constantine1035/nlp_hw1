from __future__ import annotations

import re
from typing import Iterable, List

import pandas as pd


def clean_email(text: str) -> str:
    if not isinstance(text, str):
        return ""
    parts = text.split("\n\n", 1)
    body = parts[1] if len(parts) > 1 else parts[0]

    body = body.lower()

    body = re.sub(r"http\S+|www\.\S+", " ", body)

    body = re.sub(r"\S+@\S+", " ", body)

    body = re.sub(r"[^a-z\s\.,!?']", " ", body)

    body = re.sub(r"\s+", " ", body).strip()

    return body


def tokenize(text: str) -> List[str]:
    return text.split() if text else []


def preprocess_dataframe(df: pd.DataFrame, text_col: str = "message") -> List[List[str]]:
    cleaned = df[text_col].apply(clean_email)
    corpus: List[List[str]] = []
    for msg in cleaned:
        if not msg:
            continue
        tokens = tokenize(msg)
        if tokens:
            corpus.append(tokens)
    return corpus