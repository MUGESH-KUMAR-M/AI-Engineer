"""
Document chunker using LangChain's RecursiveCharacterTextSplitter.

Splits raw document pages into smaller, overlapping chunks while
preserving the original source metadata (filename + page number).
"""

import logging
from typing import TypedDict

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# ----- defaults ---------------------------------------------------------
_CHUNK_SIZE = 500
_CHUNK_OVERLAP = 50
# -------------------------------------------------------------------------


class DocumentChunk(TypedDict):
    """Shape of a single text chunk with provenance metadata."""

    text: str
    source_filename: str
    page_number: int


def chunk_documents(
    documents: list[dict],
    chunk_size: int = _CHUNK_SIZE,
    chunk_overlap: int = _CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    """Split a list of raw document dicts into smaller chunks.

    Parameters
    ----------
    documents:
        Output of :func:`backend.rag.loader.load_pdfs`.
    chunk_size:
        Maximum character length of each chunk.
    chunk_overlap:
        Number of overlapping characters between consecutive chunks.

    Returns
    -------
    list[DocumentChunk]
        Smaller chunks, each retaining its ``source_filename`` and
        ``page_number``.
    """
    if not documents:
        logger.warning("No documents provided for chunking.")
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )

    chunks: list[DocumentChunk] = []

    for doc in documents:
        text: str = doc["text"]
        filename: str = doc["source_filename"]
        page: int = doc["page_number"]

        split_texts = splitter.split_text(text)
        for fragment in split_texts:
            chunks.append(
                DocumentChunk(
                    text=fragment,
                    source_filename=filename,
                    page_number=page,
                )
            )

    logger.info(
        "Chunked %d document page(s) into %d chunk(s) "
        "(size=%d, overlap=%d).",
        len(documents),
        len(chunks),
        chunk_size,
        chunk_overlap,
    )
    return chunks
