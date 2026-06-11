from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.vector_store import init_vector_store
from app.api.routes import documents, query, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_vector_store()
    yield


app = FastAPI(
    title="RAG Demo API",
    description="Retrieval-Augmented Generation backend with document ingestion and semantic search",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])
