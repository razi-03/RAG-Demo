from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.rag import QueryRequest, QueryResponse
from app.services.rag_service import run_rag_query, run_rag_stream

router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Run a RAG query and return the answer with sources."""
    if request.stream:
        return StreamingResponse(
            run_rag_stream(request.question, request.top_k, request.doc_id),
            media_type="text/event-stream",
        )
    return await run_rag_query(request.question, request.top_k, request.doc_id)


@router.get("/stream")
async def query_stream(question: str, top_k: int = 5, doc_id: str | None = None):
    """GET endpoint for SSE streaming (useful for EventSource in browser)."""
    return StreamingResponse(
        run_rag_stream(question, top_k, doc_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
