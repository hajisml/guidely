"""Document management endpoints."""

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from config import DOCS_DIR
from models.record import DocumentMeta
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
