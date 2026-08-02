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
