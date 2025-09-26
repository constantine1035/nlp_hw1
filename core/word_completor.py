"""Word completion using a prefix tree and word frequencies.

This module defines a :class:`WordCompletor` class that takes a token
corpus, builds a vocabulary and computes word frequencies.  It wraps a
prefix tree for efficient prefix lookups and returns both candidate
completions and their relative frequencies when queried.

The probabilities returned by :meth:`get_words_and_probs` are
*unnormalised* relative frequencies; they sum to 1 across the entire
vocabulary but not necessarily across the returned subset.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Tuple

from .trie import PrefixTree


class WordCompletor:
    """Construct a word completer from a tokenised corpus.

    Parameters
    ----------
    corpus:
        An iterable of token sequences (each sequence corresponds to a
        document/email).  Words are extracted from these sequences to
        form the vocabulary and to compute frequencies.
    min_freq:
        Words that appear fewer than ``min_freq`` times in the corpus
        are ignored when building the vocabulary.  This can be useful
        when dealing with very large corpora to keep the trie size
        manageable.  Defaults to 1 (no filtering).
    """

    def __init__(self, corpus: Iterable[Iterable[str]], min_freq: int = 1) -> None:
        self.counter: Counter[str] = Counter()
        for doc in corpus:
            self.counter.update(doc)
        # Apply frequency threshold if specified.
        if min_freq > 1:
            self.counter = Counter({w: c for w, c in self.counter.items() if c >= min_freq})
        self.total_count: int = sum(self.counter.values()) if self.counter else 0
        # Build the prefix tree from the vocabulary.
        vocabulary = list(self.counter.keys())
        self.prefix_tree = PrefixTree(vocabulary)

    def get_words_and_probs(self, prefix: str) -> Tuple[List[str], List[float]]:
        """Return candidate word completions and their relative frequencies.

        Given a prefix string, this method queries the underlying
        :class:`PrefixTree` for all words beginning with that prefix and
        computes their probabilities as ``freq(word) / total_count``.

        Probabilities are returned unnormalised across the returned subset;
        they will sum to the fraction of the total mass represented by
        those words.

        Parameters
        ----------
        prefix:
            A prefix string.  If empty, all words in the vocabulary
            will be returned (though this is rarely useful in practice).

        Returns
        -------
        tuple[list[str], list[float]]
            A tuple of two lists of equal length: the candidate words and
            their corresponding probabilities.
        """
        if not prefix:
            # Return the entire vocabulary if no prefix supplied.
            words = list(self.counter.keys())
        else:
            words = self.prefix_tree.search_prefix(prefix)
        # Compute probabilities relative to the entire corpus.  Avoid
        # division by zero if the corpus was empty.
        if not words or self.total_count == 0:
            return [], []
        probs = [self.counter[w] / self.total_count for w in words]
        return words, probs