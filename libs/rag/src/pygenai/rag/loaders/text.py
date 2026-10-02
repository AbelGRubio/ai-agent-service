"""Plain text document loader.

========================================================================================================================
Name:         pygenai/rag/loaders/text.py
Description:  Loads plain-text documents into a single Document instance.
Project:      Pygenai
Date:         2026-10-02 12:29:54
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

from pathlib import Path

from pygenai.rag.data import Document
from pygenai.rag.loaders.base import FileDocumentLoader


class TextLoader(FileDocumentLoader):
    """Loader for plain-text sources."""

    file_extensions = (".txt", ".log")

    def load(self, source: str | Path, *, encoding: str = "utf-8") -> list[Document]:
        """Read a text file and wrap it as a single document."""
        path = Path(source)
        content = self._read_text_file(path, encoding=encoding)
        metadata = self._metadata_from_path(path)
        return [Document(id=self._build_document_id(path), text=content.strip(), metadata=metadata, source=str(path))]
