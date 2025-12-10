🚀 Just built **Discovery Search** – a hybrid indexing & retrieval service that makes searching
your codebases, docs, and technical content *blazing fast and precise*!
Next Step after Data Extraction using VLM based OCR .
Here's what makes it special:
✅
**Core Features:**
Ingests from strings, files (txt/md/pdf), directories✅ Smart chunking: paragraph-aware + fixed-size sliding windows
✅ **Hybrid search**: BM25 lexical + semantic embeddings (fusion scoring)
✅ Clean FastAPI API: `/ingest` → `/search` in seconds
**The Magic:**
```
Query: "how to implement indexing pipeline"
→ Returns exact chunks + metadata + relevance scores
```
**Architecture at a glance:**
```
Docs/Code → Ingestion Pipeline → Chunks → BM25 + Embeddings → Hybrid Ranker →
Precise Results
```
**Why this matters for devs & teams:**
- Tired of grep + Google across scattered repos/docs?
- Need symbol-aware search but embeddings miss exact matches?
- Want one service for Cursor, Claude Code, *and* your custom agents?
**Next steps in roadmap:**
- Postgres/pgvector persistence
- MCP server for agent integration
- Code symbol extraction + reference graphs
- Distributed ingestion workers

#RAG #SemanticSearch #FastAPI #Python #AIEngineering #CodeIntelligence