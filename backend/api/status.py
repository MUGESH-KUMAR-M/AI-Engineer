"""
System status API — real-time health for UI indicators.
"""

import logging

import requests
from fastapi import APIRouter

from backend.config.settings import get_settings
from backend.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)
router = APIRouter()


def _check_ollama(base_url: str) -> dict:
    """Probe Ollama daemon and configured model."""
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=3)
        resp.raise_for_status()
        models = [m.get("name", "") for m in resp.json().get("models", [])]
        settings = get_settings()
        model = settings.MODEL_NAME.replace("ollama-", "")
        available = any(model in m or m.startswith(model.split(":")[0]) for m in models)
        return {
            "online": True,
            "models": models,
            "configured_model": model,
            "model_ready": available,
        }
    except Exception as exc:
        logger.debug("Ollama health check failed: %s", exc)
        return {
            "online": False,
            "models": [],
            "configured_model": get_settings().MODEL_NAME,
            "model_ready": False,
        }


@router.get("/api/status")
async def system_status() -> dict:
    """Return live status for vector DB, LLM, and RAG configuration."""
    settings = get_settings()

    try:
        store = VectorStore()
        chunk_count = store._collection.count()
        vector_ok = True
    except Exception:
        chunk_count = 0
        vector_ok = False

    ollama_status = (
        _check_ollama(settings.OLLAMA_API_URL)
        if settings.MODEL_PROVIDER == "ollama"
        else None
    )

    llm_ready = True
    if settings.MODEL_PROVIDER == "ollama" and ollama_status:
        llm_ready = ollama_status["online"] and ollama_status["model_ready"]

    return {
        "status": "ok" if vector_ok and chunk_count > 0 and llm_ready else "degraded",
        "rag": {
            "chunks": chunk_count,
            "vector_db": "chromadb",
            "embedding_model": "all-MiniLM-L6-v2"
            if settings.EMBEDDING_PROVIDER == "huggingface"
            else "text-embedding-3-small",
            "top_k": settings.TOP_K,
        },
        "llm": {
            "provider": settings.MODEL_PROVIDER,
            "model": settings.MODEL_NAME,
            "ready": llm_ready,
        },
        "ollama": ollama_status,
    }
