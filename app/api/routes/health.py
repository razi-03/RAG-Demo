from fastapi import APIRouter
from app.db.vector_store import get_collection

router = APIRouter()


@router.get("/health")
async def health():
    try:
        count = get_collection().count()
        return {"status": "ok", "vector_store": "connected", "total_chunks": count}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}
