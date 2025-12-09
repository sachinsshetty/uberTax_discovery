Below is a minimal but working “Discovery v0” in a single file, showing basic ingestion, chunking,
BM25 + semantic search, and a FastAPI HTTP API over it.[1][2][3]
## Features included
- Ingest plain text “documents” via an API.
- Simple paragraph-based chunking.
- BM25 lexical index using `rank-bm25`. [4][5]
- Semantic index using `sentence-transformers` + cosine similarity (in-memory). [1][2]
- Hybrid retrieval: BM25 + embeddings with simple score fusion.
- FastAPI endpoints: `POST /documents`, `GET /search`. [6][3][7]