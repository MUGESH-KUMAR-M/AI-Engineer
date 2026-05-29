"""
ChromaDB vector-store wrapper.

Provides a thin, application-specific API over a persistent Chroma
collection for storing and querying document embeddings.
"""

import logging
from typing import Any

import chromadb

from backend.config.settings import get_settings

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "sws_ai_documents"


class VectorStore:
    """Manage a single ChromaDB collection backed by on-disk persistence."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        self._collection = self._client.get_or_create_collection(
            name=_COLLECTION_NAME,
        )
        logger.info(
            "VectorStore ready — collection='%s', path='%s', existing docs=%d",
            _COLLECTION_NAME,
            settings.CHROMA_PATH,
            self._collection.count(),
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def add_documents(
        self,
        chunks: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> None:
        """Upsert document chunks into the collection.

        Parameters
        ----------
        chunks:
            The raw text of each chunk.
        embeddings:
            Pre-computed embedding vectors (one per chunk).
        metadatas:
            Metadata dicts (``source_filename``, ``page_number``).
        ids:
            Unique identifiers for each chunk.
        """
        self._collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        logger.info("Upserted %d document(s) into the vector store.", len(ids))

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def search(
        self,
        query_embedding: list[float],
        k: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return the *k* most similar documents for a query embedding.

        Parameters
        ----------
        query_embedding:
            The embedding vector of the user's question.
        k:
            Number of results to return.  Defaults to ``settings.TOP_K``.

        Returns
        -------
        list[dict]
            Each dict contains ``text`` and ``metadata`` keys.
        """
        settings = get_settings()
        k = k or settings.TOP_K

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )

        documents: list[dict[str, Any]] = []
        # Chroma returns lists-of-lists; we only sent one query.
        for text, meta in zip(
            results["documents"][0],
            results["metadatas"][0],
        ):
            documents.append({"text": text, "metadata": meta})

        logger.info("Vector search returned %d result(s).", len(documents))
        return documents
