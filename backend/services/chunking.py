"""Split document text into chunks small enough for embedding."""

CHUNK_WORDS = 250
OVERLAP_WORDS = 40


def chunk_text(text: str, chunk_words: int = CHUNK_WORDS, overlap_words: int = OVERLAP_WORDS) -> list[str]:
    """Pack whole paragraphs up to the word budget, overlapping the last one.

    Falls back to a plain sliding window when a single paragraph is longer
    than the budget.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current: list[str] = []
    count = 0
    for para in paragraphs:
        para_words = len(para.split())
        if para_words > chunk_words:
            if current:
                chunks.append("\n\n".join(current))
                current, count = [], 0
            chunks.extend(_sliding_window(para, chunk_words, overlap_words))
            continue
        if count + para_words > chunk_words and current:
            chunks.append("\n\n".join(current))
            # keep the last paragraph as overlap so context carries over
            current = [current[-1], para] if len(current) > 1 else [para]
            count = sum(len(p.split()) for p in current)
        else:
            current.append(para)
            count += para_words
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def _sliding_window(text: str, chunk_words: int, overlap_words: int) -> list[str]:
    words = text.split()
    if len(words) <= chunk_words:
        return [" ".join(words)]
    chunks = []
    step = chunk_words - overlap_words
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start : start + chunk_words]))
        if start + chunk_words >= len(words):
            break
    return chunks
