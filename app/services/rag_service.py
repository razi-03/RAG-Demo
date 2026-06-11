from app.core.config import settings
from app.db.vector_store import query_chunks
from app.services.embedding_service import embed_query
from app.services.llm_service import generate_answer, stream_answer
from app.schemas.rag import SourceChunk, QueryResponse


async def run_rag_query(
    question: str,
    top_k: int | None = None,
    doc_id: str | None = None,
) -> QueryResponse:
    k = top_k or settings.TOP_K
    query_embedding = await embed_query(question)

    where = {"doc_id": doc_id} if doc_id else None
    results = query_chunks(query_embedding, n_results=k, where=where)

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    # Convert cosine distance → similarity score (1 - distance)
    sources: list[SourceChunk] = []
    context_parts: list[str] = []

    for doc_text, meta, dist in zip(docs, metas, distances):
        score = round(1 - dist, 4)
        if score < settings.SIMILARITY_THRESHOLD:
            continue
        sources.append(
            SourceChunk(
                doc_id=meta.get("doc_id", ""),
                filename=meta.get("filename", ""),
                chunk_index=int(meta.get("chunk_index", 0)),
                content=doc_text,
                score=score,
            )
        )
        context_parts.append(
            f"[Source: {meta.get('filename', 'unknown')}]\n{doc_text}"
        )

    context = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant context found."
    answer = await generate_answer(question, context)

    return QueryResponse(question=question, answer=answer, sources=sources)


async def run_rag_stream(
    question: str,
    top_k: int | None = None,
    doc_id: str | None = None,
):
    """Yields SSE-formatted strings for streaming responses."""
    import json
    k = top_k or settings.TOP_K
    query_embedding = await embed_query(question)

    where = {"doc_id": doc_id} if doc_id else None
    results = query_chunks(query_embedding, n_results=k, where=where)

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    sources: list[dict] = []
    context_parts: list[str] = []

    for doc_text, meta, dist in zip(docs, metas, distances):
        score = round(1 - dist, 4)
        if score < settings.SIMILARITY_THRESHOLD:
            continue
        sources.append({
            "doc_id": meta.get("doc_id", ""),
            "filename": meta.get("filename", ""),
            "chunk_index": int(meta.get("chunk_index", 0)),
            "content": doc_text,
            "score": score,
        })
        context_parts.append(f"[Source: {meta.get('filename')}]\n{doc_text}")

    # First event: sources metadata
    yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"

    context = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant context found."

    async for token in stream_answer(question, context):
        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"
