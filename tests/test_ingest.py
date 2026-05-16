"""Tests for markdown ingestion and chunking."""

from pathlib import Path

from second_brain.ingest import (
    Chunk,
    chunk_text,
    ingest_directory,
    iter_markdown_files,
)


def test_chunk_text_short_document_is_one_chunk() -> None:
    assert chunk_text("A short paragraph.") == ["A short paragraph."]


def test_chunk_text_groups_paragraphs() -> None:
    text = "Para one.\n\nPara two.\n\nPara three."
    chunks = chunk_text(text, max_chars=1000)
    assert len(chunks) == 1
    assert "Para one." in chunks[0]
    assert "Para three." in chunks[0]


def test_chunk_text_splits_when_over_limit() -> None:
    para = "x" * 50
    text = f"{para}\n\n{para}\n\n{para}"
    chunks = chunk_text(text, max_chars=60)
    assert len(chunks) == 3


def test_chunk_text_hard_splits_oversized_paragraph() -> None:
    chunks = chunk_text("y" * 250, max_chars=100)
    assert len(chunks) == 3
    assert all(len(c) <= 100 for c in chunks)


def test_chunk_text_empty_document() -> None:
    assert chunk_text("") == []


def test_iter_markdown_files(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("# A", encoding="utf-8")
    (tmp_path / "b.markdown").write_text("# B", encoding="utf-8")
    (tmp_path / "c.txt").write_text("not markdown", encoding="utf-8")
    sub = tmp_path / "nested"
    sub.mkdir()
    (sub / "d.md").write_text("# D", encoding="utf-8")

    found = list(iter_markdown_files(tmp_path))
    names = sorted(p.name for p in found)
    assert names == ["a.md", "b.markdown", "d.md"]


def test_ingest_directory(tmp_path: Path) -> None:
    (tmp_path / "note.md").write_text(
        "First paragraph.\n\nSecond paragraph.", encoding="utf-8"
    )
    chunks = ingest_directory(tmp_path)
    assert len(chunks) >= 1
    assert all(isinstance(c, Chunk) for c in chunks)
    assert all(c.source.suffix == ".md" for c in chunks)
