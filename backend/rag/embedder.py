"""
Text embedder supporting multiple providers.

Supports: OpenAI Embeddings, HuggingFace sentence-transformers (local, no API key).
Wraps embedding services with automatic batching.
"""

import logging
from typing import Final

from backend.config.settings import get_settings

logger = logging.getLogger(__name__)

_OPENAI_MODEL: Final[str] = "text-embedding-3-small"
_HUGGINGFACE_MODEL: Final[str] = "sentence-transformers/all-MiniLM-L6-v2"
_MAX_BATCH_SIZE: Final[int] = 100


class Embedder:
    """Wrapper around embedding endpoints.

    Supports:
    - OpenAI API (requires API key, fast, high quality)
    - HuggingFace sentence-transformers (local, free, good quality)
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._provider = settings.EMBEDDING_PROVIDER or "huggingface"
        self._model = _HUGGINGFACE_MODEL

        if self._provider == "openai":
            import openai
            self._client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            self._model = _OPENAI_MODEL
            logger.info("Embedder initialised with provider=openai, model=%s", self._model)
        else:
            # HuggingFace (local, no API key needed)
            from sentence_transformers import SentenceTransformer
            self._client = SentenceTransformer(self._model)
            logger.info("Embedder initialised with provider=huggingface, model=%s", self._model)

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts, batching automatically.

        Parameters
        ----------
        texts:
            Plain-text strings to embed.

        Returns
        -------
        list[list[float]]
            One embedding vector per input text, in the same order.
        """
        if not texts:
            return []

        if self._provider == "openai":
            return self._embed_openai(texts)
        else:
            return self._embed_huggingface(texts)

    def _embed_openai(self, texts: list[str]) -> list[list[float]]:
        """Embed using OpenAI API."""
        import openai
        
        all_embeddings: list[list[float]] = []

        for start in range(0, len(texts), _MAX_BATCH_SIZE):
            batch = texts[start : start + _MAX_BATCH_SIZE]
            logger.debug(
                "Embedding batch %d–%d of %d texts (OpenAI) …",
                start + 1,
                start + len(batch),
                len(texts),
            )
            try:
                response = self._client.embeddings.create(
                    input=batch,
                    model=self._model,
                )
                batch_embeddings = [
                    item.embedding for item in response.data
                ]
                all_embeddings.extend(batch_embeddings)
            except openai.OpenAIError:
                logger.exception(
                    "OpenAI embedding request failed for batch starting at index %d",
                    start,
                )
                raise

        logger.info("Embedded %d text(s) successfully (OpenAI).", len(all_embeddings))
        return all_embeddings

    def _embed_huggingface(self, texts: list[str]) -> list[list[float]]:
        """Embed using HuggingFace sentence-transformers (local, no API key)."""
        logger.debug("Embedding %d text(s) with HuggingFace (local) …", len(texts))
        try:
            embeddings = self._client.encode(texts, convert_to_tensor=False)
            # Convert numpy arrays to lists
            result = [emb.tolist() for emb in embeddings]
            logger.info("Embedded %d text(s) successfully (HuggingFace).", len(result))
            return result
        except Exception:
            logger.exception("HuggingFace embedding failed.")
            raise

