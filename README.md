# second-brain

> Local-first personal knowledge system. Ingest your notes, search them semantically, ask questions in natural language — all running on your own machine.

## Why

I want to search my own writing the way I search the web: by meaning, not just keywords. Existing tools either require cloud APIs (privacy concerns) or are search-only (no synthesis). This runs entirely offline.

## Status

🚧 Early development. See [Roadmap](#roadmap).

## Roadmap

- [ ] **v0.1** — CLI: ingest a folder of markdown, embed locally, semantic search
- [ ] **v0.2** — Hybrid retrieval (vector + BM25)
- [ ] **v0.3** — Local LLM synthesis via Ollama
- [ ] **v0.4** — Web UI
- [ ] **v0.5** — Additional sources: RSS, browser bookmarks
- [ ] **v1.0** — Docker compose deployment, encrypted sync

## Architecture

See [docs/architecture.md](docs/architecture.md).

## License

MIT
