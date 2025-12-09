A practical way to build this is as a modular Python service with four main subsystems:
ingestion, indexing, retrieval, and serving (HTTP + MCP). [1][2][3]
## 1. Plan project structure
Design a monorepo-friendly, service-oriented layout:
- `nia_server/`: core package
- `ingestion/`: Git, HTTP, filesystem, PDF, HTML parsers
- `chunking/`: code/document chunking heuristics
- `indexing/`: BM25, embeddings, symbol index, reference graph, regex/file-tree search
- `retrieval/`: hybrid ranking, graph walks, snippet assembly
- `session/`: session state and snippet-acceptance tracking
- `mcp/`: MCP server implementation and schemas
- `api/`: HTTP/JSON API (FastAPI)
- `models/`: Pydantic models for queries, results, config
- `storage/`: DB and vector-store abstraction
- `scripts/`: CLI tools for crawling and backfilling sources
- `tests/`: unit/integration tests
Use Python 3.11+, FastAPI for HTTP, SQLAlchemy + Postgres (or SQLite to start), and a vector
DB (Qdrant, pgvector, or similar) for embeddings. [2][3][4]
## 2. Implement ingestion pipelines
1. **Source registry and config**
- Create a `Source` table with fields: `id`, `type` (`git`, `docs_http`, `pdf`, `wiki`), `url_or_path`,
`metadata` JSON, `default_branch`, `enabled`.
- Add a small CLI (Typer) to register sources and trigger ingestion runs.
2. **Fetchers**
- Git: use `gitpython` to clone/update repos into a local cache directory keyed by `source_id`.
- HTTP docs/SDK pages: use `httpx` or `requests` with rate limiting; respect robots.txt and
auth where required.
- PDFs: use `pypdf` or `pdfminer.six` to extract text and basic layout.
- Local filesystem: walk directories and read files directly.
3. **Parsers and structure extraction**
- Code (Python, TS/JS, Go, etc.):
- Use language-specific parsers where possible (e.g., `ast` for Python, `tree-sitter` bindings
for multi-language) to identify functions, classes, methods, types, and docstrings. [5][6]
- Markdown/HTML docs:
- Parse headings, sections, and tables with `markdown-it-py` or `beautifulsoup4`.
- PDFs:
- Treat each page or logical section as a document, splitting by headings or large font
changes where detectable.
4. **Normalization model**
- Define a `Document` model (DB + Pydantic): `id`, `source_id`, `uri` (e.g.,
`repo://path/to/file.py#L10`), `language`, `content`, `structured_blocks` (JSON), `metadata`.
- Normalize all parsed content into this internal format before chunking.
## 3. Chunking and symbol/usage extraction
1. **Chunking strategy**
- Implement language-aware chunkers:
- Code: chunk by function/method/class or small groups of adjacent definitions; include
surrounding comments and relevant imports. [5][6]
- Docs: chunk by heading + paragraph, keeping chunk sizes within a token budget (e.g.,
512–1024 tokens). [7][4]
- Represent chunks as `Chunk` records with: `id`, `document_id`, `text`, `start_offset`,
`end_offset`, `symbol_ids` (optional), `metadata` (headings, path, language).
2. **Symbol and usage index**
- Define `Symbol` model: `id`, `source_id`, `name`, `kind` (`function`, `class`, `type`,
`endpoint`, etc.), `signature`, `uri` (file + range), `container` (module/class), `language`.
- During parsing, extract:
- Definitions (where symbol is introduced).
- References/usages (call sites, type annotations, imports).
- Store usage relations in a `SymbolUsage` or `SymbolEdge` table: `from_symbol_id`,
`to_symbol_id`, `kind` (`call`, `inherits`, `imports`, `endpoint_calls`, etc.). [5][6]
- Link each `Chunk` to associated symbols (definitions and notable usages).
3. **Basic reference graph**
- Build a graph over nodes of type `file`, `symbol`, and `external_doc_section`.
- Use edges: `defines`, `uses`, `imports`, `links_to` (for hyperlinks between docs),
`same_topic` (if same heading or section). [8][3]
- Store adjacency lists in a relational table or in a graph-friendly store (but Postgres tables are
enough initially).
## 4. Build multiple indexes
1. **BM25 / sparse index**
- Use an inverted-index library (e.g., `whoosh`, `rank-bm25`, or txtai) to build a BM25 index
over chunk texts. [1][9][10]
- Index fields: `text` (chunk content), plus boosted fields for `symbol_names`, `file_path`,
`headings`. [9]
2. **Semantic embedding index**
- Use a sentence transformer or hosted embedding model to embed chunk texts. [4]
- Store embeddings in a vector store (Qdrant, pgvector, etc.) with metadata: `chunk_id`,
`source_id`, `path`, `language`, `symbol_ids`. [2][3]
- Add metadata filters (e.g., by repo, language, path prefix) to support targeted queries. [2]
3. **Symbol index**
- For symbol-name and signature search, maintain a dedicated index (could be:
- a trigram index in Postgres,
- a small BM25 index over symbol names and docstrings, or
- both). [5][6]
4. **Regex and file-tree search**
- Implement deterministic search over raw file contents using:
- direct regex search on stored file blobs for small to medium repos, or
- ripgrep-like subprocess calls against a local checkout for larger monorepos.
- Expose a file-tree API: list sources, directories, and files, and allow retrieval of raw file
content.
## 5. Implement retrieval and ranking
1. **Query model and hints**
- Create a `SearchQuery` schema with fields:
- `query_text` (natural language)
- `source_filters` (repos, docs sets)
- `path_hint` (current file path)
- `stack_trace` (optional, for future call-stack–aware ranking)
- `symbol_hint` (symbol name or language)
- `mode` (`auto`, `symbol`, `regex`, etc.).
2. **Hybrid retrieval pipeline**
- Step 1: BM25 retrieval of top N chunks. [1][9][3]
- Step 2: Semantic retrieval of top M chunks using embeddings. [2][3][4]
- Step 3: Symbol search if query looks like a symbol (e.g., contains `Class.method`, `func(`, or
path-like patterns). [5][6]
- Step 4: Merge candidates:
- Normalize scores (e.g., z-score or min-max) across BM25 and embeddings. [2][3]
- Compute a weighted sum, with possible boosts for:
- chunks in the same repo or path subtree as `path_hint`.
- symbols directly matching query tokens.
- Step 5: Use the reference graph to expand:
- Add neighbors such as direct callees, callers, or related doc sections. [8][3]
3. **Precise location results**
- For each candidate chunk, map back to:
- file path, start/end line numbers;
- associated symbols and their definitions/usages.
- Design response flavors:
- “Snippet list” (small text chunks plus metadata).
- “Symbol results” (definition location plus a small set of usage locations, e.g., top 3).
## 6. Session and context tracking
1. **Session store**
- Implement a `Session` model: `id`, `created_at`, `user_id` (optional), `active`.
- Implement `SessionEvent` or `SessionSnippet` records capturing:
- `session_id`, `query`, `result_ids`, `accepted_snippet_ids`, timestamps, and source
metadata
2. **Agent-agnostic session IDs**
- Enable agents to pass a `session_id` to both HTTP and MCP APIs.
- Provide endpoints to:
- fetch past queries and accepted snippets for a session,
- append new events,
- use session context as soft signals in ranking (e.g., prefer previously used sources or
paths).
3. **Context reconstruction**
- Add an API call like `GET /sessions/{id}/context` that returns a compact structure
summarizing the session: selected snippets, active sources, and key symbols, so any agent can
reconstruct context easily.
## 7. HTTP API design
Use FastAPI and Pydantic:
- `POST /search`
- Input: `SearchQuery` + optional `session_id`.
- Output: ranked snippets, symbol definitions/usages, graph neighbors.
- `POST /symbols/search`
- Input: symbol string and filters.
- Output: symbol definitions and usage sites.
- `GET /sources`, `POST /sources`, `POST /sources/{id}/ingest`
- Manage and trigger ingestion.
- `GET /files/tree`, `GET /files/content`
- Navigate and fetch raw file contents.
- `GET /sessions/{id}`, `GET /sessions/{id}/context`, `POST /sessions/{id}/events`
- Session interactions.
Use dependency-injected services for `Retriever`, `Indexer`, `SessionStore`, and
`SourceManager` to keep the API layer thin.
## 8. MCP server implementation
1. **Understand MCP roles**
- MCP defines a host–client–server architecture where the MCP server exposes tools and
resources via JSON-schema–described capabilities, and clients connect these to LLM hosts.
[11][12][13][14]
2. **Choose MCP server library**
- Use an existing MCP server helper library if available (e.g., from the official MCP org or
LangChain’s MCP integration) to manage handshakes, capability discovery, and
request/response plumbing. [11][15][13][14]
3. **Define MCP tools**
- Define tools like:
- `search_docs`: map to `/search` in semantic mode.
- `search_symbols`: map to symbol-search API.
- `get_file`: retrieve file content by `uri`.
- `get_session_context`: expose session summaries.
- Provide JSON Schemas for input/output so that MCP hosts (e.g., Cursor, Claude Code,
browser-based agents) can call them. [11][15][13][14]
4. **Implement server process**
- Run the MCP server as a separate process or sidecar that connects to the same DB and
vector store as the HTTP API. [11][12]
- Implement handlers that:
- parse MCP tool invocations,
- call internal services (`Retriever`, `SessionStore`, `SourceManager`),
- return structured responses tailored for LLM consumption.
## 9. Multi-project and multi-agent support
1. **Multi-project isolation and filtering**
- Tag all sources, documents, chunks, and symbols with `project_id` or `tenant_id`.
- Ensure all retrieval queries must specify or infer a project scope, so a single deployment can
serve multiple repos and doc sets safely.
2. **Agent-agnostic behavior**
- Avoid agent-specific logic; treat all clients as generic.
- Session IDs and project IDs come from clients (Cursor, Claude Code, browser agent), which
can all attach to the same Nia instance.
3. **Config and deployment**
- Provide a single configuration file (e.g., YAML) listing DB connection, vector store,
embedding model, and ingestion schedules.
- Containerize the service with Docker; run background workers (Celery or RQ) for ingestion
and indexing jobs, and a web server for HTTP + MCP.
## 10. Testing, observability, and iteration
1. **Testing**
- Unit tests for parsers, chunkers, symbol extraction, and ranker.
- Integration tests using a small sample repo and docs, verifying that queries return the
expected definitions and usages.
2. **Observability**
- Add structured logging for ingestion runs, index updates, and search requests.
- Track metrics: ingestion latency, index size, search latency, and result click/accept rates (via
`SessionEvent`).
3. **Iterative refinement**
- Start with BM25 + embeddings hybrid retrieval, then gradually incorporate more
sophisticated graph walks and heuristic boosts as usage data accumulates. [8][2][3][4]
These steps give you a concrete path from empty repository to a working Python service that
ingests multiple sources, builds hybrid indexes plus symbol and reference graphs, exposes
precise code/doc locations, and serves multiple MCP-enabled agents over a shared,
session-aware context.
Citations:
[1] What is BM25 (Best Matching 25) Algorithm
https://www.geeksforgeeks.org/nlp/what-is-bm25-best-matching-25-algorithm/
[2] Metadata Filtering and Hybrid Search for Vector Databases
https://www.dataquest.io/blog/metadata-filtering-and-hybrid-search-for-vector-databases/
[3] generative-ai/embeddings/hybrid-search.ipynb at main
https://github.com/GoogleCloudPlatform/generative-ai/blob/main/embeddings/hybrid-search.ipy
nb
[4] Semantic Search — Sentence Transformers documentation
https://sbert.net/examples/sentence_transformer/applications/semantic-search/README.html
[5] A hands-on introduction to static code analysis
https://deepsource.com/blog/introduction-static-code-analysis
[6] pyan is a Python module that performs static analysis ... https://github.com/davidfraser/pyan
[7] BM25(llamaindex) https://aiengineering.academy/RAG/01_BM25_RAG/notebook/
[8] Classic Topic Modeling with BM25
https://dev.to/neuml/classic-topic-modeling-with-bm25-33ep
[9] Enhance Your LLM Agents with BM25: Lightweight ...
https://towardsai.net/p/artificial-intelligence/enhance-your-llm-agents-with-bm25-lightweight-retri
eval-that-works
[10] How to Create a BM25 Index in Python with Rank BM25 (Search Engine)
https://www.youtube.com/watch?v=ysvpxiPAHLg
[11] The Model Context Protocol (MCP): Deep Dive
https://www.analytical-software.de/en/the-model-context-protocol-mcp-deep-dive-into-structure-
and-concepts/
[12] What is the Model Context Protocol (MCP)? - Model Context ...
https://modelcontextprotocol.io
[13] Build an MCP server https://modelcontextprotocol.io/docs/develop/build-server
[14] Model Context Protocol https://github.com/modelcontextprotocol
[15] Model Context Protocol (MCP) - Docs by LangChain
https://docs.langchain.com/oss/python/langchain/mcp
[16] BM25 Retriever | LlamaIndex Python Documentation
https://developers.llamaindex.ai/python/examples/retrievers/bm25_retriever/
[17] How to Inspect Function and Class Signatures in Python?
https://www.gaohongnan.com/playbook/how_to_inspect_function_and_class_signatures.html
[18] How to perform static program analysis in Python for ...
https://stackoverflow.com/questions/56175087/how-to-perform-static-program-analysis-in-pytho
n-for-finding-functions-with-cert
[19] We created an open-source semantic search Python ...
https://www.reddit.com/r/Python/comments/15d1aa5/we_created_an_opensource_semantic_se
arch_python/
[20] Python static code analysis https://rules.sonarsource.com/python

