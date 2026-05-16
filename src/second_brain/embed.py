"""Embed text chunks into vectors using a local embedding model."""

from dataclasses import dataclass
from typing import Any, Protocol

from second_brain.ingest import Chunk

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


@dataclass(frozen=True, slots=True)
class EmbeddedChunk:
    """A chunk paired with its embedding vector."""

    chunk: Chunk
    vector: tuple[float, ...]


class EmbeddingBackend(Protocol):
    """Minimal interface second-brain needs from an embedding model."""

    def embed(self, documents: list[str]) -> Any:
        """Return an iterable of vectors, one per input document."""
        ...


class Embedder:
    """Embeds text into vectors using a local embedding model.

    The underlying model is loaded lazily on first use: loading takes a
    moment and downloads the model (~90 MB) on the first ever run. A
    backend can also be injected directly, which is used by the tests.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        backend: EmbeddingBackend | None = None,
    ) -> None:
        self.model_name = model_name
        self._backend = backend

    def _get_backend(self) -> EmbeddingBackend:
        backend = self._backend
        if backend is None:
            from fastembed import TextEmbedding

            backend = TextEmbedding(model_name=self.model_name)
            self._backend = backend
        return backend

    def embed_texts(self, texts: list[str]) -> list[tuple[float, ...]]:
        """Embed raw strings into vectors, preserving input order."""
        if not texts:
            return []
        raw = self._get_backend().embed(texts)
        return [tuple(float(value) for value in vector) for vector in raw]

    def embed_chunks(self, chunks: list[Chunk]) -> list[EmbeddedChunk]:
        """Embed chunks, pairing each with its vector."""
        vectors = self.embed_texts([chunk.text for chunk in chunks])
        return [
            EmbeddedChunk(chunk=chunk, vector=vector)
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
