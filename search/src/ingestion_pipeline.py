"""
Basic document ingestion + chunking pipeline for Discovery.
Features:
- Load documents from strings, files, and directories.
- Normalize into Document objects with metadata.
- Chunk documents using pluggable strategies (paragraph or fixed size).
This is in-memory and synchronous; in a scalable deployment you would:
- Run loaders + chunkers inside workers,
- Persist Documents and Chunks to DB / indices,
- Trigger indexing jobs once chunks are created.
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Dict, Optional, Protocol


# =========================
# Core data models
# =========================
@dataclass
class Document:
    id: str
    uri: str    # e.g. file path or logical identifier
    title: str
    content: str
    metadata: Dict[str, str] = field(default_factory=dict)

@dataclass
class Chunk:
    id: str
    document_id: str
    text: str
    position: int# position of chunk inside document
    metadata: Dict[str, str] = field(default_factory=dict)

# =========================
# Chunking strategies
# =========================
class Chunker(Protocol):
    """Common interface for all chunkers."""
    def chunk(self, document: Document) -> List[Chunk]:
        ...

class ParagraphChunker:
    """
    Split on blank lines. Works well for Markdown, simple text, and many docs. [web:88][web:94]
    """
    def chunk(self, document: Document) -> List[Chunk]:
        chunks: List[Chunk] = []
        raw_chunks = [p.strip() for p in document.content.split("\n\n") if p.strip()]
        for idx, text in enumerate(raw_chunks):
            chunks.append(
                Chunk(
                    id=str(uuid.uuid4()),
                    document_id=document.id,
                    text=text,
                    position=idx,
                    metadata={
                        "uri": document.uri,
                        "title": document.title,
                        **document.metadata,
                    },
                )
            )
        return chunks
    
class FixedSizeChunker:
    """
    Split into fixed-size character windows with overlap. [web:88][web:94]
    Use when you care about token limits and want predictable chunk sizes.
    """
    def __init__(self, max_chars: int = 800, overlap: int = 100):
        assert max_chars > 0
        assert 0 <= overlap < max_chars
        self.max_chars = max_chars
        self.overlap = overlap

    def chunk(self, document: Document) -> List[Chunk]:
        chunks: List[Chunk] = []
        text = document.content
        n = len(text)
        start = 0
        idx = 0

        while start < n:
            end = min(start + self.max_chars, n)
            piece = text[start:end].strip()
            if piece:
                chunks.append(
                    Chunk(
                        id=str(uuid.uuid4()),
                        document_id=document.id,
                        text=piece,
                        position=idx,
                        metadata={
                        "uri": document.uri,
                        "title": document.title,
                        **document.metadata,
                        },
                    )
                )
            idx += 1
            if end == n:
                break
                # slide window forward with overlap
            start = end - self.overlap
        return chunks
    
# =========================
# Ingestion: loaders
# =========================
class DocumentLoader(Protocol):
    """Interface for turning sources into Document objects."""
    def load(self) -> Iterable[Document]:
        ...

@dataclass
class StringDocumentLoader:
    """Load a single in-memory string as a Document."""
    text: str
    title: str = "Untitled"
    uri: str = "memory://document"
    metadata: Dict[str, str] = field(default_factory=dict)

    def load(self) -> Iterable[Document]:
        yield Document(
        id=str(uuid.uuid4()),
        uri=self.uri,
        title=self.title,
        content=self.text,
        metadata=self.metadata.copy(),
        )


@dataclass
class FileDocumentLoader:
    """
    Load one file from disk.
    txt / md: read as UTF‑8 text.
    pdf: placeholder for a real PDF parser (replace with pypdf / docling). [web:51][web:87]
    """
    path: Path
    encoding: str = "utf-8"
    metadata: Dict[str, str] = field(default_factory=dict)

    def load(self) -> Iterable[Document]:
        path = self.path
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md"}:
            text = path.read_text(encoding=self.encoding)
        elif suffix == ".pdf":
            # TODO: integrate real PDF parsing (e.g., docling or pypdf). [web:87][web:90]
            text = path.read_text(encoding=self.encoding, errors="ignore")
        else:
            # Fallback: treat as text
            text = path.read_text(encoding=self.encoding, errors="ignore")

        title = path.stem
        uri = f"file://{path.resolve()}"
        doc_meta = {
        "filename": path.name,
        "suffix": suffix,
        **self.metadata,
        }
        yield Document(
        id=str(uuid.uuid4()),
        uri=uri,
        title=title,
        content=text,
        metadata=doc_meta,
        )

@dataclass
class DirectoryDocumentLoader:
    """
    Recursively load files from a directory.
    Filters by allowed suffixes.
    """

    root: Path
    allowed_suffixes: Optional[List[str]] = None
    encoding: str = "utf-8"
    metadata: Dict[str, str] = field(default_factory=dict)

    def load(self) -> Iterable[Document]:
        allowed = (
        {s.lower() for s in self.allowed_suffixes}
        if self.allowed_suffixes is not None
        else None
        )
        for dirpath, _, filenames in os.walk(self.root):
            for name in filenames:
                path = Path(dirpath) / name
                suffix = path.suffix.lower()
                if allowed is not None and suffix not in allowed:
                    continue
                file_loader = FileDocumentLoader(
                path=path,
                encoding=self.encoding,
                metadata=self.metadata,
                )
                yield from file_loader.load()

# =========================
# Pipeline coordinator
# =========================

@dataclass
class IngestionPipeline:
    """
    Orchestrates:
    - Loading raw sources into Documents.
    - Chunking Documents with a chosen strategy. [web:54][web:89]
    For scalable Discovery:
    - Replace return with persistence to DB / indices,
    - Run in workers, driven by jobs per source or file.
    """
    chunker: Chunker
    def run_loader(self, loader: DocumentLoader) -> List[Chunk]:
        all_chunks: List[Chunk] = []
        for doc in loader.load():
            chunks = self.chunker.chunk(doc)
            all_chunks.extend(chunks)
        return all_chunks
    

# =========================
# Example usage
# =========================
if __name__ == "__main__":
    # Example 1: ingest a single string and chunk by paragraphs.
    text = """Discovery is an indexing and retrieval service.
    It builds multiple indexes over code and docs.
    This example shows how to ingest and chunk documents in Python."""
    string_loader = StringDocumentLoader(
        text=text,
        title="Discovery intro",
        uri="memory://Discovery-intro",
        metadata={"source": "example"},
    )
    pipeline = IngestionPipeline(chunker=ParagraphChunker())
    chunks = pipeline.run_loader(string_loader)

    print("Paragraph chunks:")
    for c in chunks:
        print(f"- [{c.position}] {c.text!r}")
    
    # Example 2: load all .md and .txt files under a directory and chunk by fixed size.
    root_dir = Path(".") # change to your docs directory
    dir_loader = DirectoryDocumentLoader(
        root=root_dir,
        allowed_suffixes=[".md", ".txt"],
        metadata={"source": "local_docs"},
    )

    fixed_pipeline = IngestionPipeline(chunker=FixedSizeChunker(max_chars=400, overlap=80))
    dir_chunks = fixed_pipeline.run_loader(dir_loader)
    print(f"\nLoaded {len(dir_chunks)} chunks from directory {root_dir}")

    