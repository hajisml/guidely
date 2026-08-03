"""FAISS index over chunk embeddings, persisted to disk."""

import json
from dataclasses import dataclass

import faiss
import numpy as np

from config import INDEX_DIR

INDEX_FILE = INDEX_DIR / "index.faiss"
CHUNKS_FILE = INDEX_DIR / "chunks.json"


@dataclass
class Hit:
    score: float
    doc: str
    chunk_id: int
    text: str


class VectorStore:
    def __init__(self) -> None:
        self.index: faiss.Index | None = None
        self.chunks: list[dict] = []

    @property
    def ready(self) -> bool:
        return self.index is not None and self.index.ntotal > 0

    def build(self, vectors: list[np.ndarray], chunks: list[dict]) -> None:
        """Replace the index. Vectors must be L2-normalized (inner product = cosine)."""
        matrix = np.vstack(vectors).astype(np.float32)
        self.index = faiss.IndexFlatIP(matrix.shape[1])
        self.index.add(matrix)
        self.chunks = chunks

    def search(self, vector: np.ndarray, k: int = 3) -> list[Hit]:
        if not self.ready:
            return []
        scores, ids = self.index.search(vector.reshape(1, -1).astype(np.float32), k)
        hits = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < 0:
                continue
            meta = self.chunks[idx]
            hits.append(Hit(score=float(score), doc=meta["doc"], chunk_id=meta["chunk_id"], text=meta["text"]))
        return hits

    def save(self) -> None:
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(INDEX_FILE))
        CHUNKS_FILE.write_text(json.dumps(self.chunks))

    def load(self) -> bool:
        if not (INDEX_FILE.is_file() and CHUNKS_FILE.is_file()):
            return False
        self.index = faiss.read_index(str(INDEX_FILE))
        self.chunks = json.loads(CHUNKS_FILE.read_text())
        return True


store = VectorStore()
