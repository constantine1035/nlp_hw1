from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Tuple


class NGramLanguageModel:
    def __init__(self, corpus: Iterable[Iterable[str]], n: int) -> None:
        if n < 1:
            raise ValueError("n must be at least 1 for an n‑gram model")
        self.n: int = n
        self.next_counts: Dict[Tuple[str, ...], Counter[str]] = defaultdict(Counter)
        self.context_totals: Counter[Tuple[str, ...]] = Counter()
        for sent in corpus:
            if not sent or len(sent) < n:
                continue
            for i in range(len(sent) - n):
                context = tuple(sent[i : i + n])
                next_word = sent[i + n]
                self.next_counts[context][next_word] += 1
                self.context_totals[context] += 1

    def get_next_words_and_probs(self, prefix: List[str]) -> Tuple[List[str], List[float]]:
        if len(prefix) < self.n:
            raise ValueError("Длина prefix должна быть >= n (размеру контекста).")
        context = tuple(prefix[-self.n :])
        if context not in self.next_counts:
            return [], []
        counts = self.next_counts[context]
        total = self.context_totals[context]
        words = list(counts.keys())
        probs = [counts[w] / total for w in words]
        return words, probs