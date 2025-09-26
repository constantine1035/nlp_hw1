"""Combine word completion and n‑gram prediction for text suggestion.

This module defines the :class:`TextSuggestion` class which combines
the functionality of :class:`~core.word_completor.WordCompletor` and
the :class:`~core.ngram.NGramLanguageModel` to provide real‑time
suggestions while typing.  The class offers a single method,
:meth:`suggest_text`, which accepts a partial sentence and returns
candidate continuations.
"""

from __future__ import annotations

from typing import List, Tuple, Union

from .word_completor import WordCompletor
from .ngram import NGramLanguageModel


class TextSuggestion:
    """Text suggestion engine combining word completion and n‑gram prediction."""

    def __init__(self, word_completor: WordCompletor, n_gram_model: NGramLanguageModel) -> None:
        self.word_completor = word_completor
        self.n_gram_model = n_gram_model

    def suggest_text(
        self, text: Union[str, List[str]], n_words: int = 3, n_texts: int = 1
    ) -> List[List[str]]:
        """Suggest continuations for a given partial text.

        The algorithm operates in two stages:

        1. **Word completion:** If the last token in ``text`` is only a
           prefix of a word, complete it using the
           :class:`~core.word_completor.WordCompletor`.  If there are
           multiple possible completions, the most frequent one is
           selected.
        2. **Next words:** Using the completed context as input to the
           n‑gram model, greedily predict the next ``n_words`` tokens by
           always choosing the most probable next token at each step.

        Parameters
        ----------
        text:
            Either a raw string containing the partial sentence or a
            list of tokens.  If a string is provided, it will be
            split on whitespace into tokens.
        n_words:
            The number of additional words to generate after completing
            the current word.  Defaults to 3.
        n_texts:
            The number of alternative continuations to return.  The
            current implementation always returns exactly 1 continuation
            regardless of this parameter; support for multiple
            alternatives could be added in the future.

        Returns
        -------
        list[list[str]]
            A list of continuations.  Each continuation is itself a list
            of tokens: the first token is the completed version of the
            current (possibly partial) last token, followed by up to
            ``n_words`` additional tokens predicted by the n‑gram model.
        """
        # Normalise input into a list of tokens.
        if isinstance(text, str):
            tokens = text.strip().split()
        else:
            tokens = list(text)
        if not tokens:
            return []

        # Stage 1: Complete the last token if it may be partial.
        prefix = tokens[-1]
        # Query the word completer for completions.
        cand_words, cand_probs = self.word_completor.get_words_and_probs(prefix)
        if not cand_words:
            return []
        # Choose the most frequent completion (argmax over probs).  Note: if
        # multiple completions share the same highest probability, the
        # lexicographically first is chosen via max's default tie
        # behaviour.
        best_idx = max(range(len(cand_words)), key=lambda i: cand_probs[i])
        completed = cand_words[best_idx]

        # Prepare the suggestion starting with the completed word.
        suggestion = [completed]

        # Build context for next‑word prediction.  Replace the last token
        # with the completed word and keep the preceding tokens.
        context_seq = tokens[:-1] + [completed]

        # Stage 2: Greedy next‑word prediction using the n‑gram model.
        for _ in range(n_words):
            try:
                next_words, next_probs = self.n_gram_model.get_next_words_and_probs(context_seq)
            except ValueError:
                # Not enough context to query the n‑gram model.  Stop
                # predicting additional words.
                break
            if not next_words:
                break
            # Choose the most probable next word.
            j = max(range(len(next_words)), key=lambda i: next_probs[i])
            w = next_words[j]
            suggestion.append(w)
            context_seq.append(w)
        # Currently we only support returning a single continuation.
        return [suggestion][:n_texts]