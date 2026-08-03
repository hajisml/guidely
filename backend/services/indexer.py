"""Rebuild the vector index from the documents folder."""

import logging
import time

from config import DOCS_DIR
from services.chunking import chunk_text
from services.embeddings import embed_documents
from services.parsing import is_supported, parse_file
from services.vector_store import store

log = logging.getLogger(__name__)


def rebuild_index() -> dict:
    """Chunk and embed every doc, then swap in a fresh index.

    Unchanged content is served from the embedding cache, so re-running
    this only calls the API for new or edited chunks.
    """
    started = time.perf_counter()
    files = sorted(p for p in DOCS_DIR.iterdir() if p.is_file() and is_supported(p.name))
    if not files:
        raise ValueError("no documents to index")

    chunks: list[dict] = []
    skipped: list[str] = []
    for path in files:
        try:
            text = parse_file(path)
        except ValueError as exc:
            log.warning("skipping %s: %s", path.name, exc)
            skipped.append(path.name)
            continue
        for i, chunk in enumerate(chunk_text(text)):
            chunks.append({"doc": path.name, "chunk_id": i, "text": chunk})

    if not chunks:
        raise ValueError("no readable documents to index")

    vectors = embed_documents([c["text"] for c in chunks])
    store.build(vectors, chunks)
    store.save()

    elapsed = time.perf_counter() - started
    log.info("indexed %d chunks from %d docs in %.2fs", len(chunks), len(files) - len(skipped), elapsed)
    return {
        "documents": len(files) - len(skipped),
        "skipped": skipped,
        "chunks": len(chunks),
        "seconds": round(elapsed, 2),
    }
