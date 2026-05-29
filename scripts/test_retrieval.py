"""
Quick retrieval smoke-test for the vector store.

Run from project root:

    python scripts/test_retrieval.py
    python scripts/test_retrieval.py "What is the leave policy?"
"""

import sys

from backend.rag.embedder import Embedder
from backend.rag.vector_store import VectorStore

DEFAULT_QUERY = "What is the leave policy?"


def main() -> None:
    query = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUERY
    embedder = Embedder()
    store = VectorStore()

    embedding = embedder.embed([query])[0]
    results = store.search(embedding, k=5)

    print(f"Query: {query}\n")
    if not results:
        print("No results found.")
        return

    for i, hit in enumerate(results, start=1):
        meta = hit["metadata"]
        print(f"{i}. {meta['source_filename']} (page {meta['page_number']})")
        print(f"   {hit['text'][:200].replace(chr(10), ' ')}…\n")


if __name__ == "__main__":
    main()
