"""
Chat API router.

Exposes the ``POST /api/chat`` endpoint that accepts a user question,
runs the RAG pipeline, and returns a structured response with sources.
"""

import logging

from fastapi import APIRouter, HTTPException

from backend.models.schemas import ChatRequest, ChatResponse, Source
from backend.rag.pipeline import answer as pipeline_answer

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Handle a chat question and return an AI-generated answer.

    Parameters
    ----------
    request:
        JSON body containing the user's ``question`` string.

    Returns
    -------
    ChatResponse
        The answer text together with the list of document sources.
    """
    logger.info("POST /api/chat — question=%r", request.question[:120])

    try:
        result = pipeline_answer(request.question)
        sources = [
            Source(filename=s["filename"], page=s["page"])
            for s in result.get("sources", [])
        ]
        return ChatResponse(answer=result["answer"], sources=sources)
    except Exception:
        logger.exception("Unhandled error in /api/chat")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your question.",
        )
