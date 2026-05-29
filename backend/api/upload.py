"""
Document upload and ingestion API endpoints.

Allows users to upload PDF documents dynamically without restarting the server.
Automatically chunks, embeds, and stores them in ChromaDB.
"""

import logging
import hashlib
from pathlib import Path
from typing import Any

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.rag.chunker import chunk_documents
from backend.rag.embedder import Embedder
from backend.rag.loader import RawDocument
from backend.rag.vector_store import VectorStore
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()


class UploadResponse(BaseModel):
    """Response from document upload."""
    filename: str
    pages: int
    chunks: int
    message: str


class IngestionStatus(BaseModel):
    """Status of document ingestion."""
    total_documents: int
    total_pages: int
    total_chunks: int
    vector_db_path: str


@router.post("/api/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> UploadResponse:
    """Upload and ingest a PDF document dynamically.

    The document is processed in the background while the response
    is returned immediately.

    Parameters
    ----------
    file:
        PDF file to upload (max 50MB).

    Returns
    -------
    UploadResponse
        Confirmation with document stats.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 50MB limit."
        )

    logger.info("Upload request for: %s (%d bytes)", file.filename, file.size or 0)

    try:
        # Save uploaded file
        settings = get_settings()
        upload_dir = Path(settings.PDF_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / file.filename
        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

        logger.info("Saved uploaded file: %s", file_path)

        # Process in background
        background_tasks.add_task(
            _process_uploaded_document,
            str(file_path),
            file.filename
        )

        return UploadResponse(
            filename=file.filename,
            pages=0,  # Will be updated after processing
            chunks=0,  # Will be updated after processing
            message=f"File '{file.filename}' received. Processing in background..."
        )

    except Exception as e:
        logger.exception("Upload failed for %s", file.filename)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document: {str(e)}"
        )


def _process_uploaded_document(file_path: str, filename: str) -> None:
    """Process uploaded PDF: extract, chunk, embed, and store.

    Runs in background after upload confirmation.
    """
    try:
        import fitz  # PyMuPDF

        logger.info("Processing uploaded document: %s", filename)

        # 1. Extract text from PDF
        documents: list[RawDocument] = []
        doc = fitz.open(file_path)

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text().strip()
            if text:
                documents.append(
                    RawDocument(
                        text=text,
                        source_filename=filename,
                        page_number=page_num + 1,
                    )
                )
        doc.close()

        logger.info("  → Extracted %d page(s) from %s", len(documents), filename)

        # 2. Chunk documents
        chunks = chunk_documents(documents)
        logger.info("  → Created %d chunk(s)", len(chunks))

        # 3. Embed chunks
        embedder = Embedder()
        texts = [c["text"] for c in chunks]
        embeddings = embedder.embed(texts)
        logger.info("  → Generated %d embedding(s)", len(embeddings))

        # 4. Store in vector DB
        store = VectorStore()
        ids = [
            _generate_chunk_id(c, i)
            for i, c in enumerate(chunks)
        ]
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

        logger.info(
            "✓ Successfully ingested: %s (%d pages, %d chunks)",
            filename,
            len(documents),
            len(chunks)
        )

    except Exception:
        logger.exception("Failed to process uploaded document: %s", filename)


def _generate_chunk_id(chunk: dict, index: int) -> str:
    """Create deterministic chunk ID."""
    raw = f"{chunk['source_filename']}:{chunk['page_number']}:{index}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


@router.get("/api/ingest-status", response_model=IngestionStatus)
async def get_ingestion_status() -> IngestionStatus:
    """Get current ingestion status.

    Returns information about the vector database and ingested documents.

    Returns
    -------
    IngestionStatus
        Stats about currently ingested documents.
    """
    try:
        store = VectorStore()
        count = store._collection.count()

        settings = get_settings()

        return IngestionStatus(
            total_documents=count,  # Approximation
            total_pages=count,      # Approximation
            total_chunks=count,
            vector_db_path=settings.CHROMA_PATH,
        )
    except Exception as e:
        logger.exception("Failed to get ingestion status")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get status: {str(e)}"
        )
