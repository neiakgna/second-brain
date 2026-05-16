"""Semantic search over the knowledge base."""

from pathlib import Path

from second_brain.embed import Embedder
from second_brain.store import SearchHit, Store


def search(
    query: str,
    db_path: Path,
    k: int = 5,
    embedder: Embedder | None = None,
) -> list[SearchHit]:
    """Embed `query` and return the `k` stored chunks closest to it.

    `embedder` can be supplied for testing; by default a real one is
    created (which loads the embedding model on first use).
    """
    if not query.strip():
        return []

    active_embedder = embedder or Embedder()
    query_vector = active_embedder.embed_texts([query])[0]

    store = Store(db_path)
    try:
        return store.search_vectors(query_vector, k=k)
    finally:
        store.close()
