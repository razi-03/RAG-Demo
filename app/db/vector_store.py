import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings

_client: chromadb.ClientAPI = None
_collection: chromadb.Collection = None


async def init_vector_store():
    global _client, _collection
    _client = chromadb.PersistentClient(
        path=settings.CHROMA_PERSIST_DIR,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    _collection = _client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"[VectorStore] Collection '{settings.CHROMA_COLLECTION}' ready — {_collection.count()} docs.")


def get_collection() -> chromadb.Collection:
    if _collection is None:
        raise RuntimeError("Vector store not initialised. Call init_vector_store() first.")
    return _collection


def add_chunks(
    ids: list[str],
    embeddings: list[list[float]],
    documents: list[str],
    metadatas: list[dict],
):
    col = get_collection()
    col.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)


def query_chunks(
    query_embedding: list[float],
    n_results: int,
    where: dict | None = None,
) -> dict:
    col = get_collection()
    kwargs = dict(
        query_embeddings=[query_embedding],
        n_results=min(n_results, col.count() or 1),
        include=["documents", "metadatas", "distances"],
    )
    if where:
        kwargs["where"] = where
    return col.query(**kwargs)


def delete_document_chunks(doc_id: str):
    col = get_collection()
    col.delete(where={"doc_id": doc_id})


def list_documents() -> list[dict]:
    col = get_collection()
    results = col.get(include=["metadatas"])
    seen: dict[str, dict] = {}
    for meta in results["metadatas"]:
        doc_id = meta.get("doc_id", "unknown")
        if doc_id not in seen:
            seen[doc_id] = {
                "doc_id": doc_id,
                "filename": meta.get("filename", ""),
                "chunk_count": 1,
                "uploaded_at": meta.get("uploaded_at", ""),
            }
        else:
            seen[doc_id]["chunk_count"] += 1
    return list(seen.values())
