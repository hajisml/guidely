"""Document management endpoints."""

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from google.genai import errors as genai_errors

from config import DOCS_DIR
from models.record import DocumentContent, DocumentMeta, DocumentUpdate
from services.gemini import MissingApiKeyError
from services.indexer import rebuild_index
from services.parsing import parse_bytes

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _safe_path(name: str) -> Path:
    """Resolve a document name inside DOCS_DIR, blocking path tricks."""
    if not name or name != Path(name).name or name.startswith("."):
        raise HTTPException(status_code=400, detail="invalid document name")
    return DOCS_DIR / name


def _meta(path: Path) -> DocumentMeta:
    stat = path.stat()
    return DocumentMeta(
        name=path.name,
        size=stat.st_size,
        modified=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
    )


@router.get("")
def list_documents() -> list[DocumentMeta]:
    files = sorted(p for p in DOCS_DIR.iterdir() if p.is_file())
    return [_meta(p) for p in files]


@router.post("", status_code=201)
async def upload_document(file: UploadFile) -> DocumentMeta:
    data = await file.read()
    try:
        text = parse_bytes(data, file.filename or "")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    dest = _safe_path(file.filename or "")
    dest.write_text(text, encoding="utf-8")
    return _meta(dest)


@router.post("/reindex")
def reindex() -> dict:
    try:
        return rebuild_index()
    except MissingApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except genai_errors.APIError as exc:
        raise HTTPException(status_code=502, detail=f"model request failed: {exc.message or exc.code}")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{name}")
def get_document(name: str) -> DocumentContent:
    path = _safe_path(name)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"document not found: {name}")
    return DocumentContent(name=name, content=path.read_text(encoding="utf-8"))


@router.put("/{name}")
def update_document(name: str, body: DocumentUpdate) -> DocumentMeta:
    path = _safe_path(name)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"document not found: {name}")
    if not body.content.strip():
        raise HTTPException(status_code=400, detail="content cannot be empty")
    path.write_text(body.content, encoding="utf-8")
    return _meta(path)


@router.delete("/{name}", status_code=204)
def delete_document(name: str) -> None:
    path = _safe_path(name)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"document not found: {name}")
    path.unlink()
