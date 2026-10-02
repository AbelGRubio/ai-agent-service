"""CSV document loader.

========================================================================================================================
Name:         pygenai/rag/loaders/csv.py
Description:  Converts rows from a CSV file into a single document string.
Project:      Pygenai
Date:         2026-10-02 12:29:54
Status:       Development

Copyright ©2026 All rights reserved.
========================================================================================================================
"""

from __future__ import annotations

import csv
from pathlib import Path

from pygenai.rag.data import Document
from pygenai.rag.loaders.base import FileDocumentLoader


class CSVLoader(FileDocumentLoader):
    """Loader for tabular data sources."""

    file_extensions = (".csv",)

    def load(self, source: str | Path, *, encoding: str = "utf-8") -> list[Document]:
        """Read a CSV file and turn each row into a compact text representation."""
        path = Path(source)
        rows: list[str] = []
        with path.open("r", newline="", encoding=encoding, errors="replace") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row:
                    continue
                cells = [f"{key}: {value}" for key, value in row.items() if value not in (None, "")]
                rows.append(" | ".join(cells))

        metadata = self._metadata_from_path(path, row_count=len(rows))
        text = "\n".join(rows) if rows else ""
        return [Document(id=self._build_document_id(path), text=text, metadata=metadata, source=str(path))]
