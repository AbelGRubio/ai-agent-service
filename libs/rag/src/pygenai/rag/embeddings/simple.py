"""Simple local embedding provider for tests and offline development.

========================================================================================================================
Name:         pygenai/rag/embeddings/simple.py
Description:  Provides a deterministic bag-of-words embedding implementation.
Project:      Pygenai
Date:         2026-10-02 17:05:00
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Sequence

from langchain_core.embeddings import Embeddings

from .base import BaseEmbeddings


class SimpleEmbeddings(BaseEmbeddings, Embeddings):
    """Deterministic, token-based embedding implementation used for offline use."""

    def __init__(self) -> None:
        """Initialize the embedding model with a token vocabulary."""
        self._vocabulary: list[str] = []

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Split text into lowercase tokens suitable for bag-of-words embeddings."""
        return re.findall(r"[a-z0-9]+", text.lower())

    def _vector_from_text(self, text: str, vocabulary: list[str]) -> list[float]:
        """Build a count-based vector for a given text."""
        counts = Counter(self._tokenize(text))
        return [float(counts.get(token, 0.0)) for token in vocabulary]

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """Return deterministic count-based vectors for each input text."""
        vocabulary = sorted({token for text in texts for token in self._tokenize(text)} | set(self._vocabulary))
        self._vocabulary = vocabulary
        return [self._vector_from_text(text, vocabulary) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        """Return the embedding for a single search query."""
        vocabulary = self._vocabulary or sorted(set(self._tokenize(text)))
        if not self._vocabulary:
            self._vocabulary = vocabulary
        return self._vector_from_text(text, vocabulary)
