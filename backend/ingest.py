"""
Standalone ingestion script.

Reads PDFs → chunks text → embeds with OpenAI → stores in ChromaDB.

Run from the project root:

    python -m backend.ingest
"""

import hashlib
import logging
import sys

from backend.rag.chunker import chunk_documents
from backend.rag.embedder import Embedder
from backend.rag.loader import load_pdfs
from backend.rag.vector_store import VectorStore

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def _generate_chunk_id(chunk: dict, index: int) -> str:
    """Create a deterministic, collision-resistant ID for a chunk.

    Uses a hash of the source filename, page number, and chunk index
    so that re-running ingestion upserts rather than duplicates.
    """
    raw = f"{chunk['source_filename']}:{chunk['page_number']}:{index}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def main() -> None:
    """Execute the full ingestion pipeline."""
    logger.info("=" * 60)
    logger.info("Starting document ingestion pipeline")
    logger.info("=" * 60)

    # Step 1 — Load PDFs
    logger.info("Step 1/4: Loading PDFs …")
    raw_documents = load_pdfs()
    if not raw_documents:
        logger.error("No documents loaded. Aborting.")
        sys.exit(1)
    logger.info("  → %d raw page(s) loaded.", len(raw_documents))

    # Step 2 — Chunk
    logger.info("Step 2/4: Chunking documents …")
    chunks = chunk_documents(raw_documents)
    if not chunks:
        logger.error("Chunking produced zero chunks. Aborting.")
        sys.exit(1)
    logger.info("  → %d chunk(s) created.", len(chunks))

    # Step 3 — Embed
    logger.info("Step 3/4: Generating embeddings …")
    embedder = Embedder()
    texts = [c["text"] for c in chunks]
    embeddings = embedder.embed(texts)
    logger.info("  → %d embedding(s) generated.", len(embeddings))

    # Step 4 — Store
    logger.info("Step 4/4: Storing in ChromaDB …")
    store = VectorStore()
    ids = [_generate_chunk_id(c, i) for i, c in enumerate(chunks)]
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
    logger.info("  → %d chunk(s) stored.", len(ids))

    logger.info("=" * 60)
    logger.info("Ingestion complete ✓")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
