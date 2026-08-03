"""Create embeddings for chunks and queries via Gemini."""

import numpy as np
from google.genai import types

from services.gemini import get_client

EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 768
BATCH_SIZE = 100


def _embed(texts: list[str], task_type: str) -> list[np.ndarray]:
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


def _normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    return vec / norm if norm else vec


def embed_documents(texts: list[str]) -> list[np.ndarray]:
    return _embed(texts, "RETRIEVAL_DOCUMENT")


def embed_query(text: str) -> np.ndarray:
    return _embed([text], "RETRIEVAL_QUERY")[0]
