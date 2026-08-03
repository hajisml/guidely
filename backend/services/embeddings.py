"""Create embeddings for chunks and queries via Gemini, with a local cache."""

import hashlib
import json
import logging

import numpy as np
from google.genai import types

from config import CACHE_DIR
from services.gemini import get_client

EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 768
BATCH_SIZE = 100
CACHE_FILE = CACHE_DIR / "embeddings.json"

log = logging.getLogger(__name__)

_cache: dict[str, list[float]] | None = None
cache_hits = 0
cache_misses = 0


def _load_cache() -> dict[str, list[float]]:
    global _cache
    if _cache is None:
        _cache = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.is_file() else {}
    return _cache


def _save_cache() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(_cache))


def _key(text: str, task_type: str) -> str:
    return hashlib.sha256(f"{task_type}:{text}".encode()).hexdigest()


def _normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    return vec / norm if norm else vec


def _embed_api(texts: list[str], task_type: str) -> list[np.ndarray]:
    client = get_client()
    vectors: list[np.ndarray] = []
    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start : start + BATCH_SIZE]
        resp = client.models.embed_content(
            model=EMBED_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=EMBED_DIM,
            ),
        )
        vectors.extend(_normalize(np.array(e.values, dtype=np.float32)) for e in resp.embeddings)
    return vectors


def _embed(texts: list[str], task_type: str) -> list[np.ndarray]:
    global cache_hits, cache_misses
    cache = _load_cache()
    keys = [_key(t, task_type) for t in texts]
    missing = [(i, t) for i, (k, t) in enumerate(zip(keys, texts)) if k not in cache]

    if missing:
        fresh = _embed_api([t for _, t in missing], task_type)
        for (i, _), vec in zip(missing, fresh):
            cache[keys[i]] = vec.tolist()
        _save_cache()

    hits = len(texts) - len(missing)
    cache_hits += hits
    cache_misses += len(missing)
    log.info("embeddings: %d cached, %d new", hits, len(missing))
    return [np.array(cache[k], dtype=np.float32) for k in keys]


def embed_documents(texts: list[str]) -> list[np.ndarray]:
    return _embed(texts, "RETRIEVAL_DOCUMENT")


def embed_query(text: str) -> np.ndarray:
    return _embed([text], "RETRIEVAL_QUERY")[0]
