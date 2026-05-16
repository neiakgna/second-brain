"""Tests for the SQLite-backed store."""

from pathlib import Path

from second_brain.embed import EmbeddedChunk
from second_brain.ingest import Chunk
from second_brain.store import SearchHit, Store


def _embedded(text: str, index: int, vector: tuple[float, ...]) -> EmbeddedChunk:
    chunk = Chunk(text=text, source=Path(f"{text}.md"), index=index)
    return EmbeddedChunk(chunk=chunk, vector=vector)


def test_add_and_count(tmp_path: Path) -> None:
    store = Store(tmp_path / "test.db", dim=3)
    added = store.add(
        [
            _embedded("first", 0, (1.0, 0.0, 0.0)),
            _embedded("second", 1, (0.0, 1.0, 0.0)),
        ]
    )
    assert added == 2
    assert store.count() == 2
    store.close()


def test_count_empty(tmp_path: Path) -> None:
    store = Store(tmp_path / "empty.db", dim=3)
    assert store.count() == 0
    store.close()


def test_search_returns_nearest(tmp_path: Path) -> None:
    store = Store(tmp_path / "search.db", dim=3)
    store.add(
        [
            _embedded("apple", 0, (1.0, 0.0, 0.0)),
            _embedded("banana", 1, (0.9, 0.1, 0.0)),
            _embedded("car", 2, (0.0, 0.0, 1.0)),
        ]
    )
    hits = store.search_vectors((1.0, 0.0, 0.0), k=2)
    assert len(hits) == 2
    assert all(isinstance(h, SearchHit) for h in hits)
    assert hits[0].text == "apple"
    assert hits[1].text == "banana"
    assert hits[0].distance <= hits[1].distance
    store.close()


def test_search_persists_across_connections(tmp_path: Path) -> None:
    db = tmp_path / "persist.db"
    store = Store(db, dim=3)
    store.add([_embedded("hello", 0, (1.0, 0.0, 0.0))])
    store.close()

    reopened = Store(db, dim=3)
    assert reopened.count() == 1
    hits = reopened.search_vectors((1.0, 0.0, 0.0), k=1)
    assert hits[0].text == "hello"
    reopened.close()
