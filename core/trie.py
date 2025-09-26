"""Prefix tree (trie) implementation for efficient prefix queries.

This module defines two classes: :class:`PrefixTreeNode` and
:class:`PrefixTree`.  A prefix tree (or trie) stores a set of strings
and allows quick retrieval of all strings sharing a common prefix.  It
is used in the auto‑completion component of the text suggestion system
to suggest full words matching a given prefix.

The time complexity for inserting a word of length ``L`` into the trie
is :math:`O(L)`.  Querying the trie for all words with a given prefix
``p`` of length ``n`` takes :math:`O(n + mk)`, where ``m`` is the
number of matching words and ``k`` is the average length of their
suffixes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PrefixTreeNode:
    """A single node within a prefix tree.

    Each node contains a mapping from characters to child nodes and a
    flag indicating whether the node marks the end of a word.
    """

    children: Dict[str, "PrefixTreeNode"] = field(default_factory=dict)
    is_end_of_word: bool = False


class PrefixTree:
    """A prefix tree storing a vocabulary of words.

    The tree is built from a list of words.  After construction, it
    supports efficient retrieval of all words starting with a given
    prefix via :meth:`search_prefix`.
    """

    def __init__(self, vocabulary: List[str]) -> None:
        """Construct the prefix tree from an iterable of words.

        Parameters
        ----------
        vocabulary:
            A list of unique words to insert into the trie.  If the
            vocabulary contains duplicates, they are silently
            deduplicated.
        """
        self.root = PrefixTreeNode()
        # Insert each word into the trie.  Using a set ensures we don't
        # insert the same word multiple times, which would have no
        # effect on the tree structure but would waste time.
        for word in set(vocabulary):
            self._insert(word)

    def _insert(self, word: str) -> None:
        """Insert a single word into the prefix tree."""
        node = self.root
        for char in word:
            # Descend or create child node.
            if char not in node.children:
                node.children[char] = PrefixTreeNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search_prefix(self, prefix: str) -> List[str]:
        """Return all words in the trie starting with a given prefix.

        Parameters
        ----------
        prefix:
            The prefix to search for.  If the prefix is empty, all
            words in the trie are returned (this behaviour is not
            generally used in the context of the suggestion system but
            follows naturally from the tree structure).

        Returns
        -------
        list[str]
            All words that begin with ``prefix``.  If no word matches,
            an empty list is returned.
        """
        node = self.root
        # Traverse down the trie following the characters of the prefix.
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        # Collect all words under this prefix.
        results: List[str] = []
        self._collect_words(node, prefix, results)
        return results

    def _collect_words(self, node: PrefixTreeNode, prefix: str, results: List[str]) -> None:
        """Depth‑first traversal collecting all words from a given node.

        Parameters
        ----------
        node:
            The current node in the traversal.
        prefix:
            The prefix accumulated so far that identifies the path to
            ``node``.  When ``node.is_end_of_word`` is ``True``, this
            prefix represents a complete word.
        results:
            A list to append complete words to as they are discovered.
        """
        if node.is_end_of_word:
            results.append(prefix)
        for char, child in node.children.items():
            self._collect_words(child, prefix + char, results)