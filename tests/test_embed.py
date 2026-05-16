"""Tests for the embedding layer."""

import os
from pathlib import Path

import pytest

from second_brain.embed import (
    EMBEDDING_DIM,
    EmbeddedChunk,
    Embedder,
)
from second_brain.ingest import Chunk


class FakeBackend:
    """A deterministic stand-in for a real embedding model."""

    def embed(self, documents: list[str]) -> list[list[float]]:
        return [[float(len(doc)), 1.0, 2.0] for doc in documents]


def _chunk(text: str, index: int) -> Chunk:
    return Chunk(text=text, source=Path("note.md"), index=index)


def test_embed_texts_empty_returns_empty() -> None:
    embedder = Embedder(backend=FakeBackend())
    assert embedder.embed_texts([]) == []


def test_embed_texts_one_vector_per_text() -> None:
    embedder = Embedder(backend=FakeBackend())
    vectors = embedder.embed_texts(["a", "bb", "ccc"])
    assert len(vectors) == 3
    assert all(isinstance(v, tuple) for v in vectors)
    assert vectors[0][0] == 1.0
    assert vectors[2][0] == 3.0


def test_embed_chunks_pairs_and_preserves_order() -> None:
    embedder = Embedder(backend=FakeBackend())
    chunks = [_chunk("first", 0), _chunk("second", 1)]
    embedded = embedder.embed_chunks(chunks)
    assert len(embedded) == 2
    assert all(isinstance(e, EmbeddedChunk) for e in embedded)
    assert embedded[0].chunk is chunks[0]
    assert embedded[1].chunk is chunks[1]


def test_embed_chunks_empty() -> None:
    embedder = Embedder(backend=FakeBackend())
    assert embedder.embed_chunks([]) == []


@pytest.mark.skipif(
    not os.environ.get("SB_RUN_SLOW_TESTS"),
    reason="set SB_RUN_SLOW_TESTS=1 to run tests that load the real model",
)
def test_real_model_produces_correct_dimension() -> None:
    embedder = Embedder()
    vectors = embedder.embed_texts(["hello world"])
    assert len(vectors) == 1
    assert len(vectors[0]) == EMBEDDING_DIM
