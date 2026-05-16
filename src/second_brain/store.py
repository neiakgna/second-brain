"""Persist embedded chunks in a local SQLite database with vector search."""

import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

import sqlite_vec  # type: ignore[import-untyped]  # no type stubs published

from second_brain.embed import EMBEDDING_DIM, EmbeddedChunk


@dataclass(frozen=True, slots=True)
class SearchHit:
    """A stored chunk returned from a vector search, with its distance."""

    text: str
    source: Path
    chunk_index: int
    distance: float


def _connect(path: Path) -> sqlite3.Connection:
    """Open a SQLite connection with the sqlite-vec extension loaded."""
    conn = sqlite3.connect(path)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn


class Store:
    """A SQLite-backed store for embedded chunks with vector search."""

    def __init__(self, path: Path, dim: int = EMBEDDING_DIM) -> None:
        self.path = path
        self.dim = dim
        self._conn = _connect(path)
        self._create_schema()

    def _create_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY,
                text TEXT NOT NULL,
                source TEXT NOT NULL,
                chunk_index INTEGER NOT NULL
            )
            """
        )
        self._conn.execute(
            f"CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks "
            f"USING vec0(embedding float[{self.dim}])"
        )
        self._conn.commit()

    def add(self, embedded: Iterable[EmbeddedChunk]) -> int:
        """Insert embedded chunks into the store. Returns the count inserted."""
        count = 0
        for item in embedded:
            cursor = self._conn.execute(
                "INSERT INTO chunks (text, source, chunk_index) VALUES (?, ?, ?)",
                (item.chunk.text, str(item.chunk.source), item.chunk.index),
            )
            row_id = cursor.lastrowid
            if row_id is None:
                raise RuntimeError("INSERT did not return a row id")
            self._conn.execute(
                "INSERT INTO vec_chunks (rowid, embedding) VALUES (?, ?)",
                (row_id, sqlite_vec.serialize_float32(list(item.vector))),
            )
            count += 1
        self._conn.commit()
        return count

    def count(self) -> int:
        """Return the number of chunks currently stored."""
        row = self._conn.execute("SELECT COUNT(*) FROM chunks").fetchone()
        return int(row[0])

    def search_vectors(self, query_vector: Sequence[float], k: int = 5) -> list[SearchHit]:
        """Return the `k` stored chunks closest to `query_vector`."""
        rows = self._conn.execute(
            """
            SELECT c.text, c.source, c.chunk_index, v.distance
            FROM vec_chunks v
            JOIN chunks c ON c.id = v.rowid
            WHERE v.embedding MATCH ? AND k = ?
            ORDER BY v.distance
            """,
            (sqlite_vec.serialize_float32(list(query_vector)), k),
        ).fetchall()
        return [
            SearchHit(
                text=row[0],
                source=Path(row[1]),
                chunk_index=int(row[2]),
                distance=float(row[3]),
            )
            for row in rows
        ]

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()
