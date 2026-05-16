# ADR 0001: Embedding library

## Status

Accepted

## Context

second-brain needs to turn text into vector embeddings for semantic
search. The obvious default is `sentence-transformers`, the most widely
used library for this task.

However, `sentence-transformers` depends on PyTorch. On Windows, the
default PyTorch wheel bundles CUDA and is over 2 GB. second-brain is
meant to be a lightweight, local-first tool that is quick to install on
any machine. A multi-gigabyte dependency works against that goal.

## Decision

Use `fastembed` instead of `sentence-transformers`.

`fastembed` runs embedding models through ONNX Runtime rather than
PyTorch. It supports the same `all-MiniLM-L6-v2` model (384-dimensional
vectors) with an install footprint of roughly 100 MB.

The embedding model is accessed only through the `EmbeddingBackend`
protocol in `embed.py`, so the concrete library can be swapped later
without touching the rest of the codebase.

## Consequences

- Install size drops from ~2 GB to ~100 MB.
- No GPU acceleration. For the expected workload (embedding personal
  notes) CPU inference is fast enough.
- The `EmbeddingBackend` protocol keeps the door open to other backends
  if a future need arises.
