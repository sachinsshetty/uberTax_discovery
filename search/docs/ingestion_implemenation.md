Ingestion Module

Provide code for document ingestion and chunking pipeline
Below is a compact, production‑ready starting point for a document ingestion + chunking
pipeline in Python, designed to plug into your Nia prototype’s indexing layer.[1][2][3]

## Overview
- Load documents from:
- in‑memory strings,
- individual files,
- directories (recursive, suffix‑filtered).[1][2]
- Normalize to `Document` objects with metadata.
- Apply pluggable chunkers:
- paragraph‑based,
- fixed‑size sliding window.[3][4]

You can now plug the returned `Chunk` objects straight into your BM25 and embedding
indexers from the earlier Nia prototype, and later swap in more advanced loaders (e.g., Git,
HTTP docs) and chunkers (heading‑aware, code‑aware) without changing downstream
code.[2][3][5]
Citations:
[1] Building Document Parsing Pipelines with Python - SA Space
https://saspace.substack.com/p/building-document-parsing-pipelines
[2] Tutorial: Preprocessing Different File Types - Haystack
https://haystack.deepset.ai/tutorials/30_file_type_preprocessing_index_pipeline
[3] Chunking Strategies to Improve Your RAG Performance
https://weaviate.io/blog/chunking-strategies-for-rag
[4] Semantic search using text chunking
https://docs.opensearch.org/latest/tutorials/vector-search/semantic-search/long-document/
[5] Pipelines - Haystack Documentation https://docs.haystack.deepset.ai/v2.1/docs/pipelines