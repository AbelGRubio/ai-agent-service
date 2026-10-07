"""PDF document loader.

========================================================================================================================
Name:         pygenai/rag/loaders/pdf.py
Description:  Extracts text from PDF files using pypdf when available.
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


class PDFLoader(FileDocumentLoader):
    """Loader for PDF files."""

    file_extensions = (".pdf",)

    def load(self, source: str | Path, *, encoding: str = "utf-8") -> list[Document]:
        """Extract text from a PDF source and return it as one document."""
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover - optional dependency path
            msg = "PDF parsing requires the optional dependency 'pypdf'. Install it with 'uv add pypdf'."
            raise ImportError(msg) from exc

        path = Path(source)
        reader = PdfReader(str(path))
        texts: list[str] = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")

        metadata = self._metadata_from_path(path, page_count=len(reader.pages))
        text = "\n\n".join(texts)
        return [Document(id=self._build_document_id(path), text=text, metadata=metadata, source=str(path))]
