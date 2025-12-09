Below is a minimal but working “Discovery v0” in a single file, showing basic ingestion, chunking,
BM25 + semantic search, and a FastAPI HTTP API over it.[1][2][3]
## Features included
- Ingest plain text “documents” via an API.
- Simple paragraph-based chunking.
- BM25 lexical index using `rank-bm25`. [4][5]
- Semantic index using `sentence-transformers` + cosine similarity (in-memory). [1][2]
- Hybrid retrieval: BM25 + embeddings with simple score fusion.
- FastAPI endpoints: `POST /documents`, `GET /search`. [6][3][7]

This file gives you a runnable baseline: you can ingest documents, query with simple hybrid
search, and later evolve it into the full Nia design (symbol index, reference graph, sessions,
MCP server, incremental ingestion, etc.).[8][6][9]

Citations:
[1] How to Implement Semantic Search in Python Step by Step
https://www.pingcap.com/article/semantic-search-python-step-by-step/
[2] How do I implement semantic search with Python?
https://milvus.io/ai-quick-reference/how-do-i-implement-semantic-search-with-python
[3] A Close Look at a FastAPI Example Application
https://realpython.com/fastapi-python-web-apis/
[4] BM25 for Python: Achieving high performance while simplifying ...
https://huggingface.co/blog/xhluca/bm25s
[5] rank-bm25 https://pypi.org/project/rank-bm25/
[6] Instant Semantic Search API: SQLite FTS5 + Python FastAPI
https://blog.stackademic.com/instant-semantic-search-api-sqlite-fts5-python-fastapi-3298c67769
35
[7] Bigger Applications - Multiple Files https://fastapi.tiangolo.com/tutorial/bigger-applications/
[8] How to Build a Semantic Search Engine in Python
https://www.deepset.ai/blog/how-to-build-a-semantic-search-engine-in-python
[9] Building a Semantic Search Engine from Scratch
https://learning.rabbitt.ai/blog/building-a-semantic-search-engine-from-scratch
[10] Build a semantic search engine with LangChain
https://docs.langchain.com/oss/python/langchain/knowledge-base
[11] Semantic Search with Pinecone and OpenAI
https://www.datacamp.com/tutorial/semantic-search-pinecone-openai
[12] A Python implementation of the BM25 ranking function. https://github.com/nhirakawa/BM25
[13] FastAPI Project Structure Best Practices
https://www.linkedin.com/pulse/fastapi-project-structure-best-practices-manikandan-parasurama
n-fx4pc
[14] Minimalistic and local first semantic search and chat with ...
https://www.reddit.com/r/Python/comments/16thg8x/minimalistic_and_local_first_semantic_sear
ch_and/
[15] How to Create a BM25 Index in Python with Rank BM25 (Search Engine)
https://www.youtube.com/watch?v=ysvpxiPAHLg
[16] Structuring a FastAPI Project: Best Practices - DEV Community
https://dev.to/mohammad222pr/structuring-a-fastapi-project-best-practices-53l6
[17] Structuring FastAPI application with multiple services using 3 ...
https://viktorsapozhok.github.io/fastapi-oauth2-postgres/
[18] semantic-search-engine https://github.com/topics/semantic-search-engine
[19] BM25 Example https://github.com/ev2900/BM25_Search_Example
[20] Semantic Search with Vector Databases (FAISS, ChromaDB ...
https://blog.langformers.com/semantic-search/