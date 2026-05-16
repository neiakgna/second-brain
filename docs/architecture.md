# Architecture

> Status: early development. This document grows with the project.

## Overview

second-brain is a local-first knowledge system. All data and computation
stay on the user's machine — nothing is sent to the cloud unless the user
explicitly enables optional sync.

## Components

_Documented as they are built:_

- **Ingestion** — walks source directories, chunks documents
- **Embedding** — converts text chunks to vectors using a local model
- **Store** — persists vectors and metadata (sqlite-vec)
- **Search** — semantic + keyword retrieval
- **Synthesis** — local LLM answers questions over retrieved context

## Decisions

Architecture Decision Records will be added under `docs/adr/` as
significant choices are made.
