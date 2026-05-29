"""
FastAPI application entry-point.

Configures CORS, mounts API routers, and exposes a health-check
endpoint.  Run with:

    uvicorn backend.main:app --reload
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.chat import router as chat_router
from backend.api.providers import (
    configure_provider,
    list_providers,
    router as providers_router,
)
from backend.api.status import router as status_router
from backend.api.upload import (
    router as upload_router,
    upload_bulk,
    upload_document,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SWS AI RAG Chatbot API",
    version="1.0.0",
    description="Retrieval-Augmented Generation backend for company policy Q&A.",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(status_router)
app.include_router(providers_router)

# Explicit routes (ensures providers work even if an old worker cached routers)
app.add_api_route("/api/providers", list_providers, methods=["GET"], tags=["providers"])
app.add_api_route(
    "/api/providers/configure",
    configure_provider,
    methods=["POST"],
    tags=["providers"],
)
app.add_api_route("/api/upload", upload_document, methods=["POST"], tags=["upload"])
app.add_api_route("/api/upload/bulk", upload_bulk, methods=["POST"], tags=["upload"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health() -> dict[str, str]:
    """Simple liveness probe."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Startup event
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def _on_startup() -> None:
    logger.info("🚀 SWS AI RAG Chatbot API is starting up …")
    logger.info("Health-check available at GET /api/health")
    logger.info("Provider settings: GET /api/providers, POST /api/providers/configure")
    logger.info("Upload: POST /api/upload, POST /api/upload/bulk")
