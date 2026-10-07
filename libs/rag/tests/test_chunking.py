"""Unit tests for the chunking strategies."""

from __future__ import annotations

from pygenai.rag.data import Document
from pygenai.rag.chunking import FixedSizeChunker, SemanticChunker, StructureChunker, TokenChunker


def test_fixed_size_chunker_splits_by_size() -> None:
    document = Document(
        id="doc-1",
        text="alpha beta gamma delta epsilon zeta eta theta iota kappa",
        metadata={"source": "demo"},
        source="demo",
    )

    chunks = FixedSizeChunker(chunk_size=20, overlap=5).chunk_document(document)

    assert len(chunks) >= 2
    assert all(chunk.text for chunk in chunks)


def test_token_chunker_uses_word_windows() -> None:
    document = Document(id="doc-2", text="one two three four five six seven eight", metadata={})

    chunks = TokenChunker(max_tokens=3, overlap_tokens=1).chunk_document(document)

    assert len(chunks) > 1
    assert chunks[0].text.startswith("one")


def test_semantic_chunker_groups_sentences() -> None:
    document = Document(
        id="doc-3",
        text="First sentence. Second sentence. Third sentence.",
        metadata={},
    )

    chunks = SemanticChunker(max_chars=30).chunk_document(document)

    assert len(chunks) >= 1
    assert all("sentence" in chunk.text.lower() for chunk in chunks)


def test_structure_chunker_detects_headings() -> None:
    document = Document(
        id="doc-4",
        text="# Intro\nFirst section\n\n# Details\nSecond section",
        metadata={},
    )

    chunks = StructureChunker(max_chars=20).chunk_document(document)

    assert len(chunks) >= 2
    assert any("Intro" in chunk.text for chunk in chunks)
