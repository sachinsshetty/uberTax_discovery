Design a scalable ingestion and preprocessing pipeline for Discovery

A scalable ingestion and preprocessing pipeline for Discovery should be a multi-stage,
message-driven system that separates source discovery, fetch, parse, normalize, chunk, and
index update, with each stage horizontally scalable and failure-isolated.[1][2][3]
## High-level pipeline architecture
The pipeline can be modeled as an event-driven DAG:
- **Control plane**: manages source configs, schedules, and workflow orchestration.
- **Data plane**: workers subscribed to queues for each stage (fetch → parse → normalize →
chunk → embed/index).

- A central metadata store (SQL) tracks document state, and separate stores handle raw blobs
and vector/BM25 indices.[1][4][5]
Using queues (e.g., Redis, RabbitMQ, Kafka) allows each stage to scale independently and
recover from failures while preserving ordering guarantees per document or source where
needed.[1][4]
## Stages and components
1. **Source discovery and scheduling**
- A `SourceRegistry` in Postgres stores repos, HTTP doc roots, file shares, and PDFs, with
configuration like poll interval, last seen revision, and parsing options.[6][7]
- A `Scheduler` periodically enqueues “ingestion jobs” per source with a version token (e.g.,
Git commit hash, HTTP ETag, or directory snapshot ID).
2. **Fetchers (I/O heavy workers)**
- Workers consume `FetchJob` messages and:
- For Git: fetch and diff against the last indexed commit to identify changed/removed files.
- For HTTP/SDK docs: crawl sitemaps or link lists, respecting robots and using
ETags/Last-Modified to detect changes.[6][8]
- For PDFs and file shares: list and hash files to detect new/updated ones.
- Results are written as `RawDocument` entries (URI, source_id, blob location, content-type,
checksum) and “parse” tasks are enqueued per file.[4][8]
3. **Parsers (CPU-heavy workers)**
- A `ParserRouter` looks at MIME type and file extension and dispatches to specialized
parsers:
- Code parsers (Python/TS/etc.) using language-specific tools to extract AST, symbols,
docstrings.
- Markdown/HTML parsers capturing headings, sections, links, and tables.[6][8]
- PDF parsers or Docling-like tools to get structured JSON with text blocks and tables.[6][9]
- Each parser outputs a structured `ParsedDocument` (blocks, headings, symbol candidates,
metadata) stored in the DB or an object store, and emits a `NormalizeJob` message.
4. **Normalization and de-duplication**
- A `Normalizer` worker converts `ParsedDocument` to the internal `Document` model (stable
URI, language, logical sections) and ensures consistent text cleaning (case, whitespace,
normalization) that will be shared across BM25 and embedding flows.[10][11]
- It performs deduplication (e.g., by content hash) to avoid re-chunking identical docs and can
reuse embeddings when content is unchanged, which is critical for cost and throughput at
scale.[12][10]
5. **Chunking and preprocessing**
- A `Chunker` applies configurable strategies per document type:
Code: split by function/class, grouping neighboring small definitions and associated
comments.
- Docs: heading-based chunks with size limits (token or character based), preserving
structural markers.[13][7]
- For each chunk, it emits `Chunk` records (text, offsets, metadata) and enqueues `IndexJob`
messages that cover both lexical and embedding indexing.[14][13]
6. **Indexing workers (BM25 + embeddings)**
- **Lexical/BM25 indexer**: tokenizes chunk text, applies stopword filters, and updates an
inverted index (e.g., local engine or external search service), using the normalized text so lexical
and vector views stay consistent.[14][10][15]
- **Embedding indexer**: batches chunks and calls the embedding model (local or remote),
with caching keyed by content hash to avoid recomputation, then upserts vectors into the vector
DB (Qdrant, pgvector, Milvus, etc.).[13][12][3]
- Both indexers must be idempotent and able to handle out-of-order messages by checking
the latest document version in metadata before applying changes.[4][16]
## Orchestration, scaling, and reliability
- **Workflow orchestration**
- Use a workflow engine (e.g., Celery beat + queues, DBOS-style workflows, or Ray DAGs) to
define ingestion as a resilient multi-step process: fetch → parse → normalize → chunk → index,
with retries and checkpointing per document.[2][4][3]
- **Horizontal scaling**
- Run separate worker pools for `fetch`, `parse`, `chunk`, and `index` queues so each can
scale based on its CPU/IO profile; for large indexing jobs, auto-scale embedding workers and
use batch inference.[13][2][3]
- **Backpressure and prioritization**
- Limit concurrent jobs per source to avoid overloading Git servers or doc sites.
- Introduce priority queues (e.g., “hot” repos vs archival sources) so frequently used codebases
index faster.
- **State tracking and idempotency**
- Each document and chunk row includes a `version` or `generation` number; workers only
apply updates if the job’s version matches or exceeds the stored one, avoiding stale
overwrites.[4][16]
- Deletions and renames emit tombstone events so indexers can remove or update entries.
## Python implementation outline
- Use a central Postgres (or similar) DB for metadata, plus:
- object storage (S3-like) for raw and parsed blobs,
- a vector DB for embeddings,
- an optional external lexical engine (OpenSearch/Elasticsearch) or an internal BM25
implementation.[1][12][17]
- Implement workers with Celery, RQ, or Ray for distributed execution, with tasks corresponding
to the stages above.
- Provide an “ingestion API” and CLI that:
- registers sources, triggers full or incremental runs, and reports progress via document counts
and per-stage metrics.[1][4][5]
This architecture gives Nia a robust ingestion path that can grow from a single-node Python
process to a distributed pipeline capable of handling large monorepos, extensive internal wikis,
and big PDF/manual corpora while keeping BM25, embeddings, and structural metadata in
sync.
Citations:
[1] Building a Scalable Document Processing Pipeline With ... - MongoDB
https://www.mongodb.com/company/blog/technical/building-scalable-document-processing-pipel
ine-llamaparse-confluent-cloud
[2] Building Scalable RAG Pipelines with Ray and Anyscale
https://www.anyscale.com/blog/rag-pipelines-how-to
[3] Scaling Semantic Search Pipelines with Apache Spark and Vector ...
https://pub.aimind.so/scaling-semantic-search-pipelines-with-apache-spark-and-vector-databas
es-24e5724af2da
[4] Document Ingestion Pipeline | DBOS Docs
https://docs.dbos.dev/python/examples/document-detective
[5] Welcome to LlamaIndex ! | LlamaIndex Python Documentation
https://developers.llamaindex.ai/python/framework/
[6] Building Document Parsing Pipelines with Python - SA Space
https://saspace.substack.com/p/building-document-parsing-pipelines
[7] Data ingestion - .NET - Microsoft Learn
https://learn.microsoft.com/en-us/dotnet/ai/conceptual/data-ingestion
[8] Tutorial: Preprocessing Different File Types - Haystack
https://haystack.deepset.ai/tutorials/30_file_type_preprocessing_index_pipeline
[9] Docling - Docs by LangChain
https://docs.langchain.com/oss/python/integrations/document_loaders/docling
[10] How do I implement BM25 alongside vector search? - Milvusmilvus.io › ai-quick-reference ›
how-do-i-implement-bm25-alongside-vect...
https://milvus.io/ai-quick-reference/how-do-i-implement-bm25-alongside-vector-search
[11] Comparing Lexical and Semantic Vector Search Methods ...
https://arxiv.org/html/2505.11582v2
[12] Building a Semantic Search System with Apache SeaTunnel and ...
https://dev.to/seatunnel/building-a-semantic-search-system-with-apache-seatunnel-and-amazon
-bedrock-4dof
[13] How To Build High‑Performance RAG Pipelines That Scale
https://www.deepchecks.com/build-high-performance-rag-pipelines-scale/
[14] BM25(llamaindex) - AI Engineering Academy
https://aiengineering.academy/RAG/01_BM25_RAG/notebook/
[15] Mastering BM25: A Deep Dive into the Algorithm and Its ...
https://zilliz.com/learn/mastering-bm25-a-deep-dive-into-the-algorithm-and-application-in-milvus
[16] The Architect's Guide to Production RAG: Navigating Challenges ...
https://www.ragie.ai/blog/the-architects-guide-to-production-rag-navigating-challenges-and-buildi
ng-scalable-ai
[17] Scalable RAG PDF: From AWS S3 Buckets to Data Cloud Ingestion ...
https://www.linkedin.com/pulse/scalable-rag-pdf-from-aws-s3-buckets-data-cloud-ingestion-wern
er-yyjue
[18] RAG Pipeline: Example, Tools & How to Build It - lakeFS
https://lakefs.io/blog/what-is-rag-pipeline/
[19] Reranking in Hybrid Search
https://qdrant.tech/documentation/advanced-tutorials/reranking-hybrid-search/
[20] Elser
https://www.elastic.co/docs/solutions/search/semantic-search/semantic-search-elser-ingest-pipe
lines