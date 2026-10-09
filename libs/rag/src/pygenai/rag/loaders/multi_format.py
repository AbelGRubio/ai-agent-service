"""Multi-format loader factory.

========================================================================================================================
Name:         pygenai/rag/loaders/multi_format.py
Description:  Selects the most appropriate loader for a file extension.
Project:      Pygenai
Date:         2026-10-02 12:29:54
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

from pathlib import Path

from pygenai.core.data import Document
from pygenai.rag.loaders.base import FileDocumentLoader
from pygenai.rag.loaders.csv import CSVLoader
from pygenai.rag.loaders.markdown import MarkdownLoader
from pygenai.rag.loaders.pdf import PDFLoader
from pygenai.rag.loaders.text import TextLoader


class MultiFormatLoader(FileDocumentLoader):
    """Convenience loader that selects the most appropriate parser by extension."""

    file_extensions = (".txt", ".md", ".markdown", ".csv", ".pdf", ".log")

    def __init__(self) -> None:
        """Create a registry of supported format-specific loaders."""
        self._strategies: dict[str, FileDocumentLoader] = {
            ".txt": TextLoader(),
            ".log": TextLoader(),
            ".md": MarkdownLoader(),
            ".markdown": MarkdownLoader(),
            ".csv": CSVLoader(),
            ".pdf": PDFLoader(),
        }

    def load(self, source: str | Path, *, encoding: str = "utf-8") -> list[Document]:
        """Select a reader based on the file extension or raise a ValueError."""
        path = Path(source)
        suffix = path.suffix.lower()
        if suffix not in self._strategies:
            msg = f"Unsupported file type for source '{source}'."
            raise ValueError(msg)
        return self._strategies[suffix].load(path, encoding=encoding)
