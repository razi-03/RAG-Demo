import io
import uuid
import datetime
from pathlib import Path

from fastapi import UploadFile

from app.core.exceptions import UnsupportedFileTypeError

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}


def _extract_pdf(data: bytes) -> str:
    import pypdf
    reader = pypdf.PdfReader(io.BytesIO(data))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx(data: bytes) -> str:
    import docx
    doc = docx.Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)


def _extract_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


async def extract_text_from_upload(file: UploadFile) -> tuple[str, str]:
    """Returns (doc_id, extracted_text)."""
    filename = file.filename or "upload"
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(filename)

    data = await file.read()

    if ext == ".pdf":
        text = _extract_pdf(data)
    elif ext == ".docx":
        text = _extract_docx(data)
    else:
        text = _extract_text(data)

    doc_id = str(uuid.uuid4())
    return doc_id, text


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""
    chunks: list[str] = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start += chunk_size - overlap
    return chunks


def make_chunk_metadata(
    doc_id: str,
    filename: str,
    chunk_index: int,
) -> dict:
    return {
        "doc_id": doc_id,
        "filename": filename,
        "chunk_index": chunk_index,
        "uploaded_at": datetime.datetime.utcnow().isoformat(),
    }
