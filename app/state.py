from __future__ import annotations

import reflex as rx  # type: ignore
from typing import List

try:
    import pandas as pd
except ImportError:
    pd = None

from core.preprocessing import preprocess_dataframe, clean_email
from core.word_completor import WordCompletor
from core.ngram import NGramLanguageModel
from core.text_suggestion import TextSuggestion


def _load_corpus() -> List[List[str]]:
    try:
        if pd is None:
            raise ImportError("pandas is not installed")
        df = pd.read_csv("data/emails.csv")
        corpus = preprocess_dataframe(df)
        if not corpus:
            raise ValueError("Corpus is empty after preprocessing")
        return corpus
    except Exception:
        return [
            ["hello", "world"],
            ["how", "are", "you"],
            ["hello", "there"],
            ["this", "is", "a", "demo"],
        ]


_corpus = _load_corpus()
_word_completor = WordCompletor(_corpus, min_freq=1)
_ngram_model = NGramLanguageModel(_corpus, n=2)
_text_suggester = TextSuggestion(_word_completor, _ngram_model)


class State(rx.State):
    text: str = ""
    suggestions: List[str] = []
    ghost_suffix: str = ""

    @rx.event
    def update_text(self, value) -> None:
        if isinstance(value, dict):
            value = value.get("value", "")
        self.text = value

        stripped = value.lstrip()
        if not stripped:
            self.suggestions = []
            self.ghost_suffix = ""
            return

        last_char = value[-1] if value else ""
        tokens = stripped.split()

        def backfill_suggestions(existing: List[str]) -> List[str]:
            if len(existing) >= 3:
                return existing[:3]
            all_words, all_probs = _word_completor.get_words_and_probs("")
            ranked_all = sorted(zip(all_words, all_probs), key=lambda x: -x[1])
            filled = existing.copy()
            for w, _ in ranked_all:
                if w not in filled:
                    filled.append(w)
                    if len(filled) == 3:
                        break
            return filled

        if last_char.isspace():
            try:
                next_words, _ = _ngram_model.get_next_words_and_probs(tokens)
            except ValueError:
                next_words = []
            suggestions: List[str] = next_words[:3]
            suggestions = backfill_suggestions(suggestions)
            self.suggestions = suggestions
            self.ghost_suffix = suggestions[0] if suggestions else ""
        else:
            prefix = tokens[-1]
            words, probs = _word_completor.get_words_and_probs(prefix)
            ranked = sorted(zip(words, probs), key=lambda x: -x[1])
            completions: List[str] = [w for w, _ in ranked[:3]]
            suggestions: List[str] = completions.copy()
            if len(suggestions) < 3:
                try:
                    next_words, _ = _ngram_model.get_next_words_and_probs(tokens)
                except ValueError:
                    next_words = []
                for w in next_words:
                    if w not in suggestions:
                        suggestions.append(w)
                        if len(suggestions) == 3:
                            break
            suggestions = backfill_suggestions(suggestions)
            self.suggestions = suggestions
            if suggestions:
                best = suggestions[0]
                if best.startswith(prefix):
                    self.ghost_suffix = best[len(prefix):]
                else:
                    self.ghost_suffix = best
            else:
                self.ghost_suffix = ""

    @rx.event
    def apply_suggestion(self, word: str) -> None:
        current = self.text or ""
        if not current:
            self.text = word + " "
        else:
            trimmed = current.rstrip()
            if not trimmed:
                self.text = word + " "
            else:
                if current[-1].isspace():
                    self.text = current + word + " "
                else:
                    parts = trimmed.split()
                    parts[-1] = word
                    self.text = " ".join(parts) + " "
        self.update_text(self.text)

    @rx.event
    def on_key_down(self, key: str) -> None:
        if key == "Enter" and self.suggestions:
            self.apply_suggestion(self.suggestions[0])