"""
Minimal Discovery prototype: ingestion + chunking + BM25 + semantic search + HTTP API.
Requirements (install with pip):
pip install fastapi uvicorn[standard] rank-bm25 sentence-transformers scikit-learn
Run:
uvicorn Discovery_basic:app --reload
Then:
1) Add documents:
curl -X POST "http://localhost:8000/documents" \
-H "Content-Type: application/json" \
-d '{"title": "Example", "content": "First paragraph.\\n\\nSecond paragraph about Python
and FastAPI."}'
2) Search:
curl "http://localhost:8000/search?q=python"
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
import uuid
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
# -----------------------------
# Data models (in-memory store)
# -----------------------------
@dataclass
class Chunk:
    id: str
    document_id: str
    text: str
    position: int # position of chunk inside document
    metadata: Dict[str, str] = field(default_factory=dict)

@dataclass
class Document:
    id: str
    title: str
    content: str
    chunks: List[Chunk] = field(default_factory=list)

class DocumentCreate(BaseModel):
    title: str
    content: str

class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    text: str
    score: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]


# ---------------------------------
# Simple in-memory Discovery core engine
# ---------------------------------
class DiscoveryCore:
    """
    Minimal in-memory Discovery core.
    - Stores documents and chunks.
    - Maintains BM25 and embedding indices.
    - Supports hybrid search over chunks.
    """
    def __init__(self, use_embeddings: bool = True):
        self.documents: Dict[str, Document] = {}
        self.chunks: Dict[str, Chunk] = {}
        # BM25 index inputs

        self._bm25_corpus: List[List[str]] = [] # tokenized chunk texts
        self._bm25_chunks: List[str] = []
        # chunk_ids aligned with corpus
        self._bm25: Optional[BM25Okapi] = None
        # Embedding index inputs
        self.use_embeddings = use_embeddings
        self._embed_model: Optional[SentenceTransformer] = None
        self._embed_matrix = None # shape: (num_chunks, dim)
        self._embed_chunk_ids: List[str] = []
        if self.use_embeddings:
            # Tiny, fast model suitable for prototypes. [web:66]
            self._embed_model = SentenceTransformer("all-MiniLM-L6-v2")



# -------------
# Ingestion
# -------------
def add_document(self, title: str, content: str) -> str:
    """
    Add a document and update indices.
    Splits content into paragraph-like chunks (separated by blank lines).
    """
    doc_id = str(uuid.uuid4())
    doc = Document(id=doc_id, title=title, content=content)
    self.documents[doc_id] = doc
    # Simple chunking: split on blank lines.
    raw_chunks = [p.strip() for p in content.split("\n\n") if p.strip()]
    for idx, chunk_text in enumerate(raw_chunks):
        chunk_id = str(uuid.uuid4())
        chunk = Chunk(
           id=chunk_id,
        document_id=doc_id,
        text=chunk_text,
        position=idx,
        metadata={"title": title},
        )
        doc.chunks.append(chunk)
        self.chunks[chunk_id] = chunk
    # Rebuild indices naively (fine for small prototype).
    self._rebuild_bm25_index()
    if self.use_embeddings:
        self._rebuild_embedding_index()
    return doc_id

# -------------
# Indexing
# -------------
@staticmethod
def _tokenize(text: str) -> List[str]:
    """Very simple whitespace tokenizer; extend for production."""
    return text.lower().split()
def _rebuild_bm25_index(self) -> None:
    self._bm25_corpus = []
    self._bm25_chunks = []
    for chunk_id, chunk in self.chunks.items():
        tokens = self._tokenize(chunk.text)
        if not tokens:
            continue
        self._bm25_corpus.append(tokens)
        self._bm25_chunks.append(chunk_id)

    if self._bm25_corpus:
    # Build BM25 index over chunk texts. [web:71][web:74]
        self._bm25 = BM25Okapi(self._bm25_corpus)
    else:
        self._bm25 = None

def _rebuild_embedding_index(self) -> None:
    if not self.use_embeddings or self._embed_model is None:
        return
    texts = []
    chunk_ids = []

    for chunk_id, chunk in self.chunks.items():
        text = chunk.text.strip()
        if not text:
            continue
        texts.append(text)
        chunk_ids.append(chunk_id)
    if not texts:
        self._embed_matrix = None
        self._embed_chunk_ids = []
        return
    # Compute embeddings for all chunks. [web:29][web:66]
    embeddings = self._embed_model.encode(texts, show_progress_bar=False)
    self._embed_matrix = embeddings
    self._embed_chunk_ids = chunk_ids

# -------------
# Search
# -------------
def search(
    self,
    query: str,
    k: int = 5,
    alpha: float = 0.6,
    ) -> List[SearchResult]:
    """
    Hybrid search:
    - BM25 over chunks.
    - Embedding similarity over chunks.
    - Score fusion: alpha * bm25_norm + (1 - alpha) * embed_norm.
    """

    if not self.chunks:
        return []
    query_tokens = self._tokenize(query)
    # BM25 scores
    bm25_scores: Dict[str, float] = {}
    if self._bm25 is not None and query_tokens:
        scores = self._bm25.get_scores(query_tokens) # aligned with _bm25_chunks
        for chunk_id, score in zip(self._bm25_chunks, scores):
            bm25_scores[chunk_id] = float(score)
    
    # Embedding scores
    embed_scores: Dict[str, float] = {}
    if self.use_embeddings and self._embed_model is not None and self._embed_matrix is not None:
        q_emb = self._embed_model.encode([query], show_progress_bar=False)
        sims = cosine_similarity(q_emb, self._embed_matrix)[0] # shape: (num_chunks,)
        for chunk_id, score in zip(self._embed_chunk_ids, sims):
            embed_scores[chunk_id] = float(score)

# Normalize scores to [0,1] per signal (min-max).
def normalize(d: Dict[str, float]) -> Dict[str, float]:
    if not d:
        return {}
    vals = list(d.values())
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return {k: 1.0 for k in d}
    return {k: (v - lo) / (hi - lo) for k, v in d.items()}


# --------------------
# FastAPI integration
# --------------------
app = FastAPI(title="Discovery Minimal Prototype")
# Single global engine for demo.
Discovery_core = DiscoveryCore(use_embeddings=True)
@app.post("/documents", response_model=str)
def add_document(doc: DocumentCreate):
    """
    Ingest a document into Discovery.
    Returns a document ID.
    """
    if not doc.content.strip():
        raise HTTPException(status_code=400, detail="Document content cannot be empty.")
    doc_id = Discovery_core.add_document(doc.title, doc.content)
    return doc_id

@app.get("/search", response_model=SearchResponse)
def search(q: str = Query(..., min_length=1), k: int = Query(5, ge=1, le=20)):
    """
    Hybrid search over all ingested chunks.
    """
    results = Discovery_core.search(query=q, k=k)
    return SearchResponse(query=q, results=results)

@app.get("/documents/{doc_id}", response_model=DocumentCreate)
def get_document(doc_id: str):
    """
    Fetch a document (raw) by ID.
    """
    doc = Discovery_core.documents.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentCreate(title=doc.title, content=doc.content)