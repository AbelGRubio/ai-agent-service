"""OpenAI-backed embedding provider.

========================================================================================================================
Name:         pygenai/rag/embeddings/openai.py
Description:  Adapter for OpenAI embeddings using LangChain's OpenAIEmbeddings client.
Project:      Pygenai
Date:         2026-10-02 17:05:00
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

try:
    from langchain_openai import OpenAIEmbeddings as LangChainOpenAIEmbeddings
except ImportError as exc:  # pragma: no cover - optional dependency
    msg = "langchain-openai is required to use OpenAI embeddings."
    raise ImportError(msg) from exc

from .base import BaseEmbeddings


class OpenAIEmbeddingsAdapter(BaseEmbeddings, LangChainOpenAIEmbeddings):
    """Thin wrapper over LangChain's OpenAI embeddings implementation."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = "text-embedding-3-small",
        base_url: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Create the underlying OpenAI embeddings client.

        Args:
            api_key: API key for the provider. When omitted, LangChain reads the
                standard OpenAI environment variables.
            model: Name of the embedding model to call.
            base_url: Optional custom OpenAI-compatible endpoint.
            **kwargs: Extra keyword arguments forwarded to LangChain's OpenAI embeddings client.
        """
        params: dict[str, Any] = {"model": model, **kwargs}
        if api_key is not None:
            params["api_key"] = api_key
        if base_url is not None:
            params["openai_api_base"] = base_url
        super().__init__(**params)

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """Return embeddings for a sequence of document texts."""
        return super().embed_documents(list(texts))

    def embed_query(self, text: str) -> list[float]:
        """Return the embedding for a single query string."""
        return super().embed_query(text)
