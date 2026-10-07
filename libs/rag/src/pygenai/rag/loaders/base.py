"""Abstract interfaces and helpers for document loaders.

========================================================================================================================
Name:         pygenai/rag/loaders/base.py
Description:  Defines a common loader contract for transforming raw files or URLs into Document objects.
Project:      Pygenai
Date:         2026-10-02 12:19:24
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from pygenai.rag.data import Document


class DocumentLoader(ABC):
    """Abstract contract for sources that can be materialized into documents."""

    @abstractmethod
    def load(self, source: str | Path, *, encoding: str = "utf-8") -> list[Document]:
        """Load one source into one or more documents.

        Args:
            source: Local file path, remote URL, or another source identifier.
            encoding: Text decoding used for readable inputs.

        Returns:
            list[Document]: A list of document objects created from the source.
        """

    def load_many(self, sources: Iterable[str | Path], *, encoding: str = "utf-8") -> list[Document]:
        """Load several sources and flatten the results into one list."""
        documents: list[Document] = []
        for source in sources:
            documents.extend(self.load(source, encoding=encoding))
        return documents


class FileDocumentLoader(DocumentLoader):
    """Base class for file-backed loaders that operate on a local path."""

    file_extensions: tuple[str, ...] = ()

    def _read_text_file(self, path: str | Path, encoding: str = "utf-8") -> str:
        """Read a UTF-8 or specified-encoding text file from disk."""
        return Path(path).read_text(encoding=encoding, errors="replace")

    def _read_csv_rows(self, path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
        """Read a CSV source and return header names and row dictionaries."""
        with Path(path).open("r", newline="", encoding="utf-8", errors="replace") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            rows = [row for row in reader if row]
        return headers, rows

    def supports(self, path: str | Path) -> bool:
        """Return True when the extension matches the loader capability."""
        suffix = Path(str(path)).suffix.lower()
        return suffix in self.file_extensions

    @staticmethod
    def _build_document_id(source: str | Path, *, index: int = 0) -> str:
        """Generate a stable document identifier from a path."""
        normalized = str(source).replace("\\", "/")
        return f"{normalized}-doc-{index}"

    @staticmethod
    def _metadata_from_path(path: str | Path, **extra: Any) -> dict[str, Any]:
        """Collect metadata from a file path for downstream indexing."""
        resolved = Path(path)
        metadata: dict[str, Any] = {"path": str(resolved), "name": resolved.name, "suffix": resolved.suffix.lower()}
        metadata.update(extra)
        return metadata

    def load(self, source: str | Path, *, encoding: str = "utf-8") -> list[Document]:
        """Load a file from disk into a list of documents.

        Subclasses should override this method to parse file-specific content.
        """
        raise NotImplementedError


__all__ = ["DocumentLoader", "FileDocumentLoader"]
