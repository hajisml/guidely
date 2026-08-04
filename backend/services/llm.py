"""Draft answers from retrieved chunks with Gemini."""

from google.genai import types

from services.gemini import get_client
from services.vector_store import Hit

GEN_MODEL = "gemini-2.5-flash"

PROMPT = """You are Guidely, an internal knowledge assistant.
Answer the question using ONLY the numbered excerpts below. Be concise: 2-5 sentences.
Cite the excerpts you used inline, like [1] or [2][3]. If the excerpts do not
contain the answer, say so plainly and do not make anything up.

Excerpts:
{context}

Question: {question}

Answer:"""


def answer(question: str, hits: list[Hit]) -> str:
    context = "\n\n".join(f"[{i}] {h.doc}:\n{h.text}" for i, h in enumerate(hits, start=1))
    client = get_client()
    resp = client.models.generate_content(
        model=GEN_MODEL,
        contents=PROMPT.format(context=context, question=question),
        config=types.GenerateContentConfig(temperature=0.2),
    )
    return (resp.text or "").strip()
