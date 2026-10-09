"""Reranking strategies for improved retrieval quality.

========================================================================================================================
Name:         pygenai/rag/retrievers/rerank.py
Description:  Provides a simple no-op reranker and a lexical cross-encoder-like fallback.
Project:      Pygenai
Date:         2026-10-02 12:19:24
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pygenai.core.base_retriever import RetrievedDocument


class Reranker(ABC):
    """Interface for reordering candidate retrieval results."""

    @abstractmethod
    def rerank(self, query: str, documents: list[RetrievedDocument]) -> list[RetrievedDocument]:
        """Reorder candidates for a query."""


__all__ = ["Reranker"]
