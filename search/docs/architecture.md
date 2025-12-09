Design the high level architecture and components for Discovery in Python
Discovery in Python is best structured as a modular service with four layers: ingestion & normalization,
indexing, retrieval & ranking, and serving (HTTP + MCP), all backed by shared storage and a
session store.[1][2][3]
## Core architecture overview
At a high level, Discovery consists of:
- An ingestion layer that connects to sources (Git, docs, PDFs, wikis), parses them, and
normalizes them into internal documents and chunks.
- An indexing layer that builds and maintains multiple indexes: BM25/sparse, dense
embeddings, symbol/usage index, reference graph, and regex/file-tree search
structures.[1][2][4]
- A retrieval layer that runs hybrid search (BM25 + embeddings + graph signals) and assembles
precise locations (file, symbol, usage).
- A serving layer exposing a Python HTTP API (e.g. FastAPI) and a separate MCP server
process, both talking to the same storage and indices.[5][6][7]
## Ingestion and normalization layer
Components:
- **Source Manager**: manages configured sources (repos, doc sets, PDFs) and schedules
ingestion jobs.
- **Fetchers**: Git fetcher (local clones), HTTP fetcher (docs/SDK pages), filesystem/PDF
fetchers.

- **Parsers**: language-aware parsers for code, and HTML/Markdown/PDF parsers for docs,
extracting headings, sections, tables, and basic code structures.[1][8]
- **Normalizer**: converts all parsed content into a common `Document` model (URI, content,
language, structured blocks, metadata), ready for chunking and indexing.
Data flow: Source → Fetcher → Parser → Normalizer → `Document` table or collection in the
primary database (e.g. Postgres) for further processing.[9][10]
## Indexing and storage layer
Components:
- **Chunker**: splits documents into semantically meaningful chunks (functions/classes for
code, heading+paragraph for docs) with references back to original files and line ranges.[1][8]
- **Symbol & Usage Extractor**: builds a symbol catalog for functions, classes, types, and
endpoints plus their usage edges (defines, calls, imports, inherits).
- **Hybrid Search Indexes**:
- BM25/sparse index over chunk text and symbol names (e.g. in an inverted-index engine).
- Dense embedding index over chunk text stored in a vector database (e.g. pgvector/Qdrant)
with metadata filters (repo, language, path).[2][3][4]
- **Reference Graph Store**: graph over files, symbols, and doc sections (nodes) with edges
like defines, uses, imports, links_to.
- **Regex/File-tree Store**: efficient storage for raw file contents and directory structure, plus
support for regex and path-based search.
All of these share a **metadata database** (SQL) that tracks sources, documents, chunks,
symbols, and graph edges, while BM25 and vector indices store references to chunk IDs and
metadata.[9][3][11]
## Retrieval, ranking, and session layer
Components:
- **Query Router**: inspects the incoming natural language query plus hints (path, stack trace,
repo) and chooses strategies (lexical, semantic, symbol, regex, or combinations).
- **Hybrid Ranker**: runs BM25 and dense search in parallel, then merges results using a fusion
method (e.g. weighted scores or reciprocal rank fusion) and applies boosts based on hints and
session context.[3][4][11]
- **Graph Expander**: takes top chunks/symbols and walks the reference graph to add related
definitions, callers, callees, and linked docs.
- **Location Resolver**: maps chunks and symbols to concrete locations (file path, range) plus
usage sites.
- **Session Store**: records sessions keyed by `session_id`, storing queries, returned snippets,
and user-accepted snippets so any agent can reconstruct or extend context later.[5][6][7]

Data flow: Query + hints → Query Router → BM25 & vector search → Hybrid Ranker → Graph
Expander → Location Resolver → Result set, with Session Store logging selections and
providing soft signals for subsequent ranking.[3][4]
## Serving layer: HTTP API and MCP server
Components:
- **HTTP API (FastAPI)**:
- `POST /search`: main hybrid search entry point returning ranked snippets and symbol
locations.
- `POST /symbols/search`, `GET /files/tree`, `GET /files/content`, `GET/POST /sessions` to
expose symbol index, file tree, and session context to tools and agents.
- **MCP Server Process**: a separate Python process implementing MCP server semantics,
exposing Nia’s capabilities as MCP tools like `search_docs`, `search_symbols`, `get_file`, and
`get_session_context` over JSON-RPC.[5][6][12][13]
- **Multi-tenant/Project Isolation**: project or tenant identifiers carried through all layers
(sources, documents, chunks, indices, queries) so a single Nia deployment can serve multiple
repos and agents safely.
The MCP server and HTTP API are thin facades over shared application services (Retriever,
Indexer, Source Manager, Session Store), following the MCP guidance of running servers as
isolated processes that expose focused capabilities to multiple clients and agents.[5][6][7][12]
Citations:
[1] How to Build a Semantic Search Engine in Python
https://www.deepset.ai/blog/how-to-build-a-semantic-search-engine-in-python
[2] How to Implement Semantic Search in Python Step by Step - TiDB
https://www.pingcap.com/article/semantic-search-python-step-by-step/
[3] Hybrid search using vectors and full text in Azure AI Search
https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview
[4] Hybrid Search Explained https://weaviate.io/blog/hybrid-search-explained
[5] Architecture - Model Context Protocol
https://modelcontextprotocol.io/specification/2025-03-26/architecture
[6] Architecture - Model Context Protocol
https://modelcontextprotocol.io/specification/2025-06-18/architecture
[7] The Architectural Elegance of Model Context Protocol (MCP)
https://themlarchitect.com/blog/the-architectural-elegance-of-model-context-protocol-mcp/
[8] Building a Semantic Search Engine for Internal Documentation
https://blog.devgenius.io/building-a-semantic-search-engine-for-internal-documentation-a-compr
ehensive-guide-270efa9a30a0
[9] What Is Semantic Search With Filters and How to ...
https://www.tigerdata.com/blog/what-is-semantic-search-with-filters-and-how-to-implement-it-wit
h-pgvector-and-python
[10] Build a semantic search engine in Python - Vikas Paruchuri
https://www.vikas.sh/post/semantic-search-guide
[11] Building effective hybrid search in OpenSearch: Techniques and ...
https://opensearch.org/blog/building-effective-hybrid-search-in-opensearch-techniques-and-best
-practices/
[12] Introducing the Model Context Protocol - Anthropic
https://www.anthropic.com/news/model-context-protocol
[13] What Is the Model Context Protocol (MCP) and How It Works
https://www.descope.com/learn/post/mcp
[14] How to Build Your First Semantic Search System: My Step- ...
https://mlops.community/how-to-build-your-first-semantic-search-system-my-step-by-step-guide-
with-code/
[15] Introduction to Semantic Search with Python and OpenAI API
https://dev.to/carolinamonte/introduction-to-semantic-search-with-python-and-openai-api-efg
[16] Tutorial: Hybrid search with BM25 in KDB-X AI libraries - Kx Systems
https://kx.com/blog/tutorial-hybrid-search-with-bm25-in-kdb-x-ai-libraries/
[17] sagar8080/semantic-search-system https://github.com/sagar8080/semantic-search-system
[18] Building an Index that supports a hybrid search comprising of Full ...
https://github.com/run-llama/llama_index/discussions/9837
[19] Building a Semantic Code History Search with LanceDB
https://blog.continue.dev/building-a-semantic-code-history-search-with-lancedb/
[20] Semantic Search — Sentence Transformers documentation
https://sbert.net/examples/sentence_transformer/applications/semantic-search/README.html