"""
Document upload API — single or bulk via POST /api/upload.

Send one or more PDFs using form field ``file`` (repeat for multiple).
Bulk uploads use one batched embed + Chroma upsert for speed.
"""

import logging
from pathlib import Path
from typing import Union

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.config.settings import get_settings
from backend.rag.ingest_service import ingest_pdf_paths
from backend.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)
router = APIRouter()

_MAX_FILE_BYTES = 50 * 1024 * 1024
_MAX_FILES = 20


class UploadResponse(BaseModel):
    filename: str = ""
    pages: int = 0
    chunks: int = 0
    message: str
    accepted: int = 1
    files: list[dict] | None = None


class IngestionStatus(BaseModel):
    total_documents: int
    total_pages: int
    total_chunks: int
    vector_db_path: str


def _validate_pdf(file: UploadFile) -> None:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")


async def _save_upload(file: UploadFile, upload_dir: Path) -> tuple[str, str]:
    content = await file.read()
    if len(content) > _MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File '{file.filename}' exceeds 50MB limit.",
        )
    dest = upload_dir / file.filename
    dest.write_bytes(content)
    return str(dest), file.filename


def _run_ingest(paths: list[tuple[str, str]]) -> None:
    try:
        ingest_pdf_paths(paths)
    except Exception:
        logger.exception("Background ingest failed")


@router.post("/api/upload", response_model=UploadResponse)
async def upload_documents(
    background_tasks: BackgroundTasks,
    file: list[UploadFile] = File(..., description="One or more PDF files (same field name)"),
) -> UploadResponse:
    """Upload 1–20 PDFs. Multiple files are batch-indexed in one pass."""
    if not file:
        raise HTTPException(status_code=400, detail="No files provided.")

    if len(file) > _MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {_MAX_FILES} files per upload.",
        )

    settings = get_settings()
    upload_dir = Path(settings.PDF_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved: list[tuple[str, str]] = []
    file_list: list[dict] = []

    for f in file:
        _validate_pdf(f)
        path, name = await _save_upload(f, upload_dir)
        saved.append((path, name))
        file_list.append({"filename": name, "status": "queued"})
        logger.info("Upload queued: %s", name)

    background_tasks.add_task(_run_ingest, saved)

    if len(saved) == 1:
        return UploadResponse(
            filename=saved[0][1],
            accepted=1,
            message=f"'{saved[0][1]}' received. Processing in background…",
        )

    return UploadResponse(
        filename=f"{len(saved)} files",
        accepted=len(saved),
        files=file_list,
        message=f"{len(saved)} file(s) queued. Batch indexing started.",
    )


# Alias for older clients / docs
@router.post("/api/upload/bulk", response_model=UploadResponse)
async def upload_bulk_alias(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(..., description="PDF files"),
) -> UploadResponse:
    """Alias: same as POST /api/upload with multiple files."""
    return await upload_documents(background_tasks=background_tasks, file=files)


@router.get("/api/ingest-status", response_model=IngestionStatus)
async def get_ingestion_status() -> IngestionStatus:
    try:
        store = VectorStore()
        count = store._collection.count()
        settings = get_settings()
        return IngestionStatus(
            total_documents=count,
            total_pages=count,
            total_chunks=count,
            vector_db_path=settings.CHROMA_PATH,
        )
    except Exception as exc:
        logger.exception("Failed to get ingestion status")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
