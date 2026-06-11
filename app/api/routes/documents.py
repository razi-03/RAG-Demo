from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.rag import IngestResponse, DocumentMeta, DeleteResponse
from app.services.document_service import extract_text_from_upload, chunk_text, make_chunk_metadata
from app.services.embedding_service import embed_texts
from app.db.vector_store import add_chunks, delete_document_chunks, list_documents
from app.core.config import settings

router = APIRouter()


@router.post("/upload", response_model=IngestResponse)
async def upload_document(file: UploadFile = File(...)):
    """Ingest a document: extract → chunk → embed → store."""
    doc_id, text = await extract_text_from_upload(file)
    if not text.strip():
        raise HTTPException(status_code=422, detail="No text could be extracted from this file.")

    chunks = chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    embeddings = await embed_texts(chunks)

    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [make_chunk_metadata(doc_id, file.filename or "upload", i) for i in range(len(chunks))]

    add_chunks(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)

    return IngestResponse(
        doc_id=doc_id,
        filename=file.filename or "upload",
        chunk_count=len(chunks),
        message=f"Document ingested successfully into {len(chunks)} chunks.",
    )


@router.get("/", response_model=list[DocumentMeta])
async def get_documents():
    """List all ingested documents."""
    return list_documents()


@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete_document(doc_id: str):
    """Remove all chunks for a document."""
    delete_document_chunks(doc_id)
    return DeleteResponse(doc_id=doc_id, message="Document deleted successfully.")
