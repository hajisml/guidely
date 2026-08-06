"""Query logging and runtime metrics.

Every /api request is appended to a JSONL log so latency percentiles and
error counts survive restarts. Cache numbers come from the embeddings module.
"""

import json
import statistics
import time
from collections import Counter

from config import LOG_DIR
from services import embeddings
from services.vector_store import store

QUERY_LOG = LOG_DIR / "queries.jsonl"


def record_request(path: str, status: int, latency_ms: float) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": round(time.time(), 3),
        "path": path,
        "status": status,
        "latency_ms": round(latency_ms, 1),
    }
    with QUERY_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def _entries() -> list[dict]:
    if not QUERY_LOG.is_file():
        return []
    return [json.loads(line) for line in QUERY_LOG.read_text().splitlines() if line.strip()]


def summary() -> dict:
    entries = _entries()
    searches = [e for e in entries if e["path"].startswith("/api/search") and e["status"] == 200]
    latencies = [e["latency_ms"] for e in searches]
    errors = Counter(f"{e['status']} {e['path']}" for e in entries if e["status"] >= 400)

    hits, misses = embeddings.cache_hits, embeddings.cache_misses
    total_lookups = hits + misses
    return {
        "documents": len({c["doc"] for c in store.chunks}) if store.chunks else 0,
        "chunks": len(store.chunks),
        "queries_served": len(searches),
        "latency_ms": {
            "median": round(statistics.median(latencies), 1) if latencies else None,
            "p95": round(statistics.quantiles(latencies, n=20)[-1], 1) if len(latencies) >= 2 else None,
        },
        "embedding_cache": {
            "hits": hits,
            "misses": misses,
            "hit_rate": round(hits / total_lookups, 3) if total_lookups else None,
        },
        "errors": dict(errors),
    }
