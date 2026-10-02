"""Base abstractions for embedding providers.

========================================================================================================================
Name:         pygenai/rag/embeddings/base.py
Description:  Declares the common interface used by all embedding backends.
Project:      Pygenai
Date:         2026-10-02 17:05:00
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence


class BaseEmbeddings(ABC):
    """Common contract for text-to-vector embedding implementations."""

    @abstractmethod
    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """Return embeddings for a collection of documents."""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Return the embedding for a single search query."""
