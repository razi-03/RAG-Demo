import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    with patch("app.api.routes.health.get_collection") as mock_col:
        mock_col.return_value.count.return_value = 0
        resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_list_documents_empty(client):
    with patch("app.api.routes.documents.list_documents", return_value=[]):
        resp = await client.get("/api/documents/")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_query_endpoint(client):
    mock_response = MagicMock()
    mock_response.question = "What is RAG?"
    mock_response.answer = "RAG stands for Retrieval-Augmented Generation."
    mock_response.sources = []

    with patch("app.api.routes.query.run_rag_query", new_callable=AsyncMock, return_value=mock_response):
        resp = await client.post("/api/query/", json={"question": "What is RAG?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
