"""
Shared ingestion logic for single and bulk PDF uploads.

Optimizes bulk uploads by batching: extract all → chunk all → embed once → upsert once.
"""

import hashlib
import logging
from pathlib import Path
from typing import Any

import fitz

from backend.rag.chunker import chunk_documents
from backend.rag.embedder import Embedder
from backend.rag.loader import RawDocument
from backend.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

_EMBED_BATCH = 64


def _generate_chunk_id(chunk: dict, index: int) -> str:
    raw = f"{chunk['source_filename']}:{chunk['page_number']}:{index}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def extract_pdf_pages(file_path: str, filename: str) -> list[RawDocument]:
    """Extract non-empty pages from one PDF."""
    documents: list[RawDocument] = []
    doc = fitz.open(file_path)
    try:
        for page_num in range(len(doc)):
            text = doc[page_num].get_text().strip()
            if text:
                documents.append(
                    RawDocument(
                        text=text,
                        source_filename=filename,
                        page_number=page_num + 1,
                    )
                )
    finally:
        doc.close()
    return documents


def ingest_pdf_paths(file_paths: list[tuple[str, str]]) -> dict[str, Any]:
    """Ingest one or many PDFs in a single optimized pipeline.

    Parameters
    ----------
    file_paths:
        List of ``(absolute_path, source_filename)`` tuples.

    Returns
    -------
    dict
        Summary with per-file stats and totals.
    """
    if not file_paths:
        return {"files": [], "total_pages": 0, "total_chunks": 0}

    logger.info("Bulk ingest starting — %d file(s)", len(file_paths))

    all_pages: list[RawDocument] = []
    file_stats: list[dict[str, Any]] = []

    for path, filename in file_paths:
        try:
            pages = extract_pdf_pages(path, filename)
            all_pages.extend(pages)
            file_stats.append(
                {
                    "filename": filename,
                    "pages": len(pages),
                    "status": "extracted",
                }
            )
            logger.info("  ✓ %s — %d page(s)", filename, len(pages))
        except Exception as exc:
            logger.exception("Failed to extract %s", filename)
            file_stats.append(
                {
                    "filename": filename,
                    "pages": 0,
                    "status": "error",
                    "error": str(exc),
                }
            )

    if not all_pages:
        return {
            "files": file_stats,
            "total_pages": 0,
            "total_chunks": 0,
            "message": "No text extracted from uploaded PDFs.",
        }

    chunks = chunk_documents(all_pages)
    logger.info("  → %d chunk(s) from %d page(s)", len(chunks), len(all_pages))

    embedder = Embedder()
    texts = [c["text"] for c in chunks]
    embeddings: list[list[float]] = []
    for start in range(0, len(texts), _EMBED_BATCH):
        batch = texts[start : start + _EMBED_BATCH]
        embeddings.extend(embedder.embed(batch))

    store = VectorStore()
    ids = [_generate_chunk_id(c, i) for i, c in enumerate(chunks)]
    metadatas = [
        {
            "source_filename": c["source_filename"],
            "page_number": c["page_number"],
        }
        for c in chunks
    ]
    store.add_documents(
        chunks=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )

    # Update per-file chunk counts
    chunk_by_file: dict[str, int] = {}
    for c in chunks:
        name = c["source_filename"]
        chunk_by_file[name] = chunk_by_file.get(name, 0) + 1
    for stat in file_stats:
        if stat["status"] == "extracted":
            stat["chunks"] = chunk_by_file.get(stat["filename"], 0)
            stat["status"] = "indexed"

    logger.info(
        "Bulk ingest complete — %d files, %d chunks",
        len(file_paths),
        len(chunks),
    )

    return {
        "files": file_stats,
        "total_pages": len(all_pages),
        "total_chunks": len(chunks),
        "message": f"Indexed {len(chunks)} chunk(s) from {len(file_paths)} file(s).",
    }
