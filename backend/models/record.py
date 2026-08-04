"""API schemas for documents."""

from datetime import datetime

from pydantic import BaseModel


class DocumentMeta(BaseModel):
    name: str
    size: int
    modified: datetime


class DocumentContent(BaseModel):
    name: str
    content: str


class DocumentUpdate(BaseModel):
    content: str


class SearchRequest(BaseModel):
    question: str


class Source(BaseModel):
    doc: str
    chunk_id: int
    snippet: str
    score: float


class SearchResponse(BaseModel):
    answer: str
    sources: list[Source]
    latency_ms: int
