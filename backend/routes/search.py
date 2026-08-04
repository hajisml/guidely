"""Question answering over the indexed documents."""

import time

from fastapi import APIRouter, HTTPException

from models.record import SearchRequest, SearchResponse, Source
from services import llm
from services.embeddings import embed_query
from services.vector_store import store

router = APIRouter(prefix="/api/search", tags=["search"])

TOP_K = 5


def _sources(hits) -> list[Source]:
    return [
        Source(doc=h.doc, chunk_id=h.chunk_id, snippet=h.text, score=round(h.score, 3))
        for h in hits
    ]


@router.get("/similar")
def similar_chunks(q: str = "", k: int = TOP_K) -> list[Source]:
    """Raw vector similarity search, no LLM. Handy for debugging retrieval."""
    if not q.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty")
    if not store.ready:
        raise HTTPException(status_code=404, detail="no documents indexed yet, run reindex first")
    return _sources(store.search(embed_query(q.strip()), k))


@router.post("")
def search(body: SearchRequest) -> SearchResponse:
    started = time.perf_counter()
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question cannot be empty")
    if not store.ready:
        raise HTTPException(status_code=404, detail="no documents indexed yet, run reindex first")

    hits = store.search(embed_query(question), TOP_K)
    if not hits:
        raise HTTPException(status_code=404, detail="no relevant passages found for this question")

    answer = llm.answer(question, hits)
    latency_ms = int((time.perf_counter() - started) * 1000)
    return SearchResponse(answer=answer, sources=_sources(hits), latency_ms=latency_ms)
