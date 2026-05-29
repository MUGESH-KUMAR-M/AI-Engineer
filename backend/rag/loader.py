"""
PDF document loader using PyMuPDF (fitz).

Scans the configured PDF directory and extracts text from every page,
returning structured document dicts ready for the chunking stage.
"""

import logging
from pathlib import Path
from typing import TypedDict

import fitz  # PyMuPDF

from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


class RawDocument(TypedDict):
    """Shape of a single extracted document page."""

    text: str
    source_filename: str
    page_number: int


def load_pdfs(pdf_dir: str | None = None) -> list[RawDocument]:
    """Load all PDFs from *pdf_dir* and extract page-level text.

    Parameters
    ----------
    pdf_dir:
        Filesystem path to the folder containing PDFs.
        Defaults to ``settings.PDF_DIR``.

    Returns
    -------
    list[RawDocument]
        One entry per page, each containing ``text``,
        ``source_filename``, and ``page_number``.
    """
    settings = get_settings()
    directory = Path(pdf_dir or settings.PDF_DIR)

    if not directory.exists():
        logger.error("PDF directory does not exist: %s", directory)
        raise FileNotFoundError(f"PDF directory not found: {directory}")

    pdf_files = sorted(directory.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in %s", directory)
        return []

    logger.info("Found %d PDF file(s) in %s", len(pdf_files), directory)

    documents: list[RawDocument] = []

    for pdf_path in pdf_files:
        logger.info("Loading %s …", pdf_path.name)
        try:
            doc = fitz.open(str(pdf_path))
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text().strip()
                if text:
                    documents.append(
                        RawDocument(
                            text=text,
                            source_filename=pdf_path.name,
                            page_number=page_num + 1,  # 1-indexed
                        )
                    )
            doc.close()
            logger.info(
                "  ✓ Extracted %d non-empty page(s) from %s",
                sum(
                    1
                    for d in documents
                    if d["source_filename"] == pdf_path.name
                ),
                pdf_path.name,
            )
        except Exception:
            logger.exception("Failed to load %s", pdf_path.name)

    logger.info("Total raw documents extracted: %d", len(documents))
    return documents
