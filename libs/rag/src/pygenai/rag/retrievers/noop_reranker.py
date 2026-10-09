"""No-op reranker.

========================================================================================================================
Name:         pygenai/rag/retrievers/noop_reranker.py
Description:  Keeps the original retrieval order unchanged.
Project:      Pygenai
Date:         2026-10-02 12:29:54
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

from pygenai.core.base_retriever import RetrievedDocument
from pygenai.rag.retrievers.rerank import Reranker


class NoOpReranker(Reranker):
    """Keep the original retrieval order as-is."""

    def rerank(self, query: str, documents: list[RetrievedDocument]) -> list[RetrievedDocument]:
        """Return the incoming list unchanged."""
        del query
        return documents
