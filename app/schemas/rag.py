from pydantic import BaseModel, Field
from typing import Optional


# ── Documents ──────────────────────────────────────────────────────────────────

class DocumentMeta(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int
    uploaded_at: str


class IngestResponse(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int
    message: str


class DeleteResponse(BaseModel):
    doc_id: str
    message: str


# ── Query ──────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="The user's question")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="Number of chunks to retrieve")
    doc_id: Optional[str] = Field(None, description="Restrict retrieval to a specific document")
    stream: bool = Field(False, description="Stream the LLM response (SSE)")


class SourceChunk(BaseModel):
    doc_id: str
    filename: str
    chunk_index: int
    content: str
    score: float


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceChunk]
