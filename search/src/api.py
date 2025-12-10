# api.py
"""
FastAPI wrapper around Nia ingestion + index.
Endpoints:
- GET /health
: liveness check
- POST /ingest
: ingest a document (string) and index its chunks
- POST /search
: hybrid search (BM25 + embeddings)
- GET /search?q= : convenience search for manual testing [web:64][web:75]
"""

from __future__ import annotations
from dataclasses import asdict
from typing import List
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from ingestion_pipeline import (
IngestionPipeline,
ParagraphChunker,
StringDocumentLoader,
)
from core_index import DiscoveryIndex

# ---------- Pydantic models ----------
class IngestRequest(BaseModel):
    title: str
    content: str
    uri: str | None = None

class SearchRequest(BaseModel):
    query: str
    k: int = 5
    alpha: float = 0.6

class SearchHitModel(BaseModel):
    chunk_id: str
    text: str
    score: float
    metadata: dict

class SearchResponse(BaseModel):
    query: str
    results: List[SearchHitModel]

class HealthResponse(BaseModel):
    status: str


# ---------- App + single in‑memory engine (for now) ----------
app = FastAPI(title="Nia API")
nia_index = DiscoveryIndex(use_embeddings=True)
ingestion_pipeline = IngestionPipeline(chunker=ParagraphChunker())
# ---------- Endpoints ----------
@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok")

@app.post("/ingest", response_model=dict)
def ingest(req: IngestRequest):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="content must not be empty")
    loader = StringDocumentLoader(
    text=req.content,
    title=req.title,
    uri=req.uri or "memory://doc",
    metadata={},
    )
    chunks = ingestion_pipeline.run_loader(loader)
    nia_index.add_chunks(chunks)
    return {
    "ingested_chunks": len(chunks),
    "title": req.title,
    }

@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query must not be empty")
    hits = nia_index.search(req.query, k=req.k, alpha=req.alpha)
    results = [
        SearchHitModel(
            chunk_id=h.chunk_id,
            text=h.text,
            score=h.score,
            metadata=h.metadata,
            )
        for h in hits
        ]
    return SearchResponse(query=req.query, results=results)


# convenience simple GET for quick manual testing
@app.get("/search", response_model=SearchResponse)
def search_get(q: str = Query(...), k: int = Query(5, ge=1, le=20)):
    hits = nia_index.search(q, k=k)
    results = [
        SearchHitModel(
            chunk_id=h.chunk_id,
            text=h.text,
            score=h.score,
            metadata=h.metadata,
        )
    for h in hits
    ]
    return SearchResponse(query=q, results=results)