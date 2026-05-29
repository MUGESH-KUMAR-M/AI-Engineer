"""
End-to-end RAG pipeline.

Orchestrates embedding → retrieval → generation and returns a
structured result with answer text and deduplicated sources.
"""

import logging
from typing import Any

from backend.rag.embedder import Embedder
from backend.rag.llm import ask_llm
from backend.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

# Module-level singletons (lazy-initialised on first call).
_embedder: Embedder | None = None
_vector_store: VectorStore | None = None


def _get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder


def _get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def answer(question: str) -> dict[str, Any]:
    """Run the full RAG pipeline for a user question.

    Steps
    -----
    1. Embed the question using OpenAI.
    2. Retrieve the top-k most relevant chunks from ChromaDB.
    3. Pass the question + context to Claude.
    4. Deduplicate source references.

    Parameters
    ----------
    question:
        The user's natural-language question.

    Returns
    -------
    dict
        ``{"answer": str, "sources": list[{"filename": str, "page": int}]}``
    """
    logger.info("Pipeline invoked — question: %s", question[:120])

    # 1. Embed the question
    embedder = _get_embedder()
    query_embedding = embedder.embed([question])[0]

    # 2. Retrieve relevant chunks
    store = _get_vector_store()
    context_chunks = store.search(query_embedding)

    if not context_chunks:
        logger.warning("No relevant chunks found for the question.")
        return {
            "answer": "I don't have that information in the company documents.",
            "sources": [],
        }

    # 3. Generate answer
    llm_answer = ask_llm(question, context_chunks)

    # 4. Deduplicate sources (preserve insertion order)
    seen: set[tuple[str, int]] = set()
    unique_sources: list[dict[str, Any]] = []
    for chunk in context_chunks:
        meta = chunk["metadata"]
        key = (meta["source_filename"], int(meta["page_number"]))
        if key not in seen:
            seen.add(key)
            unique_sources.append(
                {"filename": key[0], "page": key[1]}
            )

    logger.info(
        "Pipeline complete — %d source(s), answer length %d chars.",
        len(unique_sources),
        len(llm_answer),
    )

    return {"answer": llm_answer, "sources": unique_sources}
