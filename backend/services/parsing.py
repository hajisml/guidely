"""Turn uploaded documents into plain text."""

from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".md"}


def is_supported(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS


def parse_bytes(data: bytes, filename: str) -> str:
    """Decode raw upload bytes, raising ValueError for anything unusable."""
    if not is_supported(filename):
        raise ValueError(f"unsupported file type: {Path(filename).suffix or 'none'}")
    if b"\x00" in data:
        raise ValueError("file looks binary, expected plain text")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("file is not valid utf-8 text") from exc
    if not text.strip():
        raise ValueError("file is empty")
    return text


def parse_file(path: Path) -> str:
    return parse_bytes(path.read_bytes(), path.name)
