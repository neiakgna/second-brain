"""Tests for semantic search orchestration."""

from pathlib import Path

from second_brain.embed import EmbeddedChunk, Embedder
from second_brain.ingest import Chunk
from second_brain.search import search
from second_brain.store import Store


class FakeBackend:
    """Returns a fixed 3-dim vector for any query used in the tests."""

    def embed(self, documents: list[str]) -> list[list[float]]:
        return [[0.95, 0.05, 0.0] for _ in documents]


def _populate(db_path: Path) -> None:
    store = Store(db_path, dim=3)
    chunk_a = Chunk(text="apple pie recipe", source=Path("food.md"), index=0)
    chunk_b = Chunk(text="fast sports car", source=Path("cars.md"), index=0)
    store.add(
        [
            EmbeddedChunk(chunk=chunk_a, vector=(1.0, 0.0, 0.0)),
            EmbeddedChunk(chunk=chunk_b, vector=(0.0, 0.0, 1.0)),
        ]
    )
    store.close()


def test_search_finds_relevant_chunk(tmp_path: Path) -> None:
    db = tmp_path / "kb.db"
    _populate(db)
    hits = search("fruit dessert", db, k=1, embedder=Embedder(backend=FakeBackend()))
    assert len(hits) == 1
    assert hits[0].text == "apple pie recipe"


def test_search_ranks_by_distance(tmp_path: Path) -> None:
    db = tmp_path / "kb.db"
    _populate(db)
    hits = search("fruit dessert", db, k=2, embedder=Embedder(backend=FakeBackend()))
    assert len(hits) == 2
    assert hits[0].text == "apple pie recipe"
    assert hits[0].distance <= hits[1].distance


def test_search_empty_query_returns_empty(tmp_path: Path) -> None:
    db = tmp_path / "kb.db"
    _populate(db)
    assert search("   ", db, embedder=Embedder(backend=FakeBackend())) == []
