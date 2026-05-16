"""Ingest markdown files: walk directories and split documents into chunks."""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

MARKDOWN_EXTENSIONS = {".md", ".markdown"}

# Target chunk size in characters. Kept under the token limit of small
# embedding models (~256 tokens, roughly 1000 characters).
DEFAULT_MAX_CHARS = 800


@dataclass(frozen=True, slots=True)
class Chunk:
    """A piece of a source document, ready for embedding."""

    text: str
    source: Path
    index: int


def iter_markdown_files(root: Path) -> Iterator[Path]:
    """Yield every markdown file under `root`, recursively, sorted by path."""
    if root.is_file():
        if root.suffix.lower() in MARKDOWN_EXTENSIONS:
            yield root
        return
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in MARKDOWN_EXTENSIONS:
            yield path


def _split_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs on blank lines, trimming whitespace."""
    parts = re.split(r"\n\s*\n", text)
    return [p.strip() for p in parts if p.strip()]


def chunk_text(text: str, max_chars: int = DEFAULT_MAX_CHARS) -> list[str]:
    """Split document text into chunks no larger than `max_chars` characters.

    Whole paragraphs are kept together where possible. A paragraph that is
    itself larger than `max_chars` is hard-split into fixed-size slices.
    """
    chunks: list[str] = []
    current = ""

    for para in _split_paragraphs(text):
        if len(para) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            for start in range(0, len(para), max_chars):
                chunks.append(para[start : start + max_chars])
            continue

        if current and len(current) + len(para) + 2 > max_chars:
            chunks.append(current)
            current = para
        elif current:
            current = f"{current}\n\n{para}"
        else:
            current = para

    if current:
        chunks.append(current)
    return chunks


def ingest_file(path: Path, max_chars: int = DEFAULT_MAX_CHARS) -> list[Chunk]:
    """Read a single markdown file and return its chunks."""
    text = path.read_text(encoding="utf-8")
    return [
        Chunk(text=chunk, source=path, index=index)
        for index, chunk in enumerate(chunk_text(text, max_chars))
    ]


def ingest_directory(root: Path, max_chars: int = DEFAULT_MAX_CHARS) -> list[Chunk]:
    """Walk `root`, read every markdown file, and return all chunks."""
    chunks: list[Chunk] = []
    for file in iter_markdown_files(root):
        chunks.extend(ingest_file(file, max_chars))
    return chunks
