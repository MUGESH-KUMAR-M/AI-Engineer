"""
Document upload and ingestion API — single file and bulk optimized upload.
"""

import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.config.settings import get_settings
from backend.rag.ingest_service import ingest_pdf_paths
from backend.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)
router = APIRouter()

_MAX_FILE_BYTES = 50 * 1024 * 1024
_MAX_BULK_FILES = 20


class UploadResponse(BaseModel):
    filename: str
    pages: int = 0
    chunks: int = 0
    message: str


class BulkFileResult(BaseModel):
    filename: str
    pages: int = 0
    chunks: int = 0
    status: str
    error: str | None = None


class BulkUploadResponse(BaseModel):
    accepted: int
    files: list[BulkFileResult]
    message: str


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


def _run_bulk_ingest(paths: list[tuple[str, str]]) -> None:
    try:
        ingest_pdf_paths(paths)
    except Exception:
        logger.exception("Bulk background ingest failed")


@router.post("/api/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> UploadResponse:
    """Upload and ingest a single PDF (background processing)."""
    _validate_pdf(file)
    settings = get_settings()
    upload_dir = Path(settings.PDF_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path, filename = await _save_upload(file, upload_dir)
    logger.info("Single upload: %s", filename)

    background_tasks.add_task(_run_bulk_ingest, [(file_path, filename)])

    return UploadResponse(
        filename=filename,
        message=f"'{filename}' received. Processing in background…",
    )


@router.post("/api/upload/bulk", response_model=BulkUploadResponse)
async def upload_bulk(
    files: list[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> BulkUploadResponse:
    """Upload multiple PDFs — one batched embed + Chroma upsert (faster than N singles)."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")
    if len(files) > _MAX_BULK_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {_MAX_BULK_FILES} files per bulk upload.",
        )

    settings = get_settings()
    upload_dir = Path(settings.PDF_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved: list[tuple[str, str]] = []
    results: list[BulkFileResult] = []

    for file in files:
        _validate_pdf(file)
        file_path, filename = await _save_upload(file, upload_dir)
        saved.append((file_path, filename))
        results.append(BulkFileResult(filename=filename, status="queued"))
        logger.info("Bulk queued: %s", filename)

    background_tasks.add_task(_run_bulk_ingest, saved)

    return BulkUploadResponse(
        accepted=len(saved),
        files=results,
        message=f"{len(saved)} file(s) queued. Optimized batch indexing started.",
    )


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
