"""Unit tests for the RAG document loaders."""

from __future__ import annotations

from pathlib import Path

from pygenai.rag.loaders import CSVLoader, MarkdownLoader, MultiFormatLoader, TextLoader, WebLoader


def test_text_loader_reads_plain_text(tmp_path: Path) -> None:
    source = tmp_path / "notes.txt"
    source.write_text("hello world\nsecond line", encoding="utf-8")

    documents = TextLoader().load(source)

    assert len(documents) == 1
    assert documents[0].text == "hello world\nsecond line"
    assert documents[0].metadata["name"] == "notes.txt"


def test_markdown_loader_keeps_format_metadata(tmp_path: Path) -> None:
    source = tmp_path / "guide.md"
    source.write_text("# Title\n\nParagraph", encoding="utf-8")

    documents = MarkdownLoader().load(source)

    assert documents[0].metadata["format"] == "markdown"
    assert "Title" in documents[0].text


def test_csv_loader_turns_rows_into_text(tmp_path: Path) -> None:
    source = tmp_path / "data.csv"
    source.write_text("name,city\nAda,London\nGrace,New York\n", encoding="utf-8")

    documents = CSVLoader().load(source)

    assert "Ada" in documents[0].text
    assert documents[0].metadata["row_count"] == 2


def test_multi_format_loader_dispatches_by_extension(tmp_path: Path) -> None:
    source = tmp_path / "multi.txt"
    source.write_text("alpha beta", encoding="utf-8")

    documents = MultiFormatLoader().load(source)

    assert documents[0].text == "alpha beta"


def test_web_loader_uses_html_extraction(monkeypatch, tmp_path: Path) -> None:  # noqa: ANN001
    source = "https://example.com"

    class _Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"<html><body><h1>Hello</h1><p>World</p></body></html>"

    def fake_urlopen(_request):
        return _Response()

    monkeypatch.setattr("pygenai.rag.loaders.web.request.urlopen", fake_urlopen)

    documents = WebLoader().load(source)

    assert documents[0].source == source
    assert "Hello" in documents[0].text
    assert "World" in documents[0].text
