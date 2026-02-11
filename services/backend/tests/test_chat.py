"""Tests for Chat API endpoint and NL processing."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.services.memory_store import _store


@pytest.fixture(autouse=True)
def clear_store():
    _store.clear()
    yield
    _store.clear()


@pytest.mark.anyio
async def test_chat_create_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/chat", json={
            "message": "Buy groceries"
        })
    assert response.status_code == 200
    data = response.json()
    assert "Buy groceries" in data["response"]
    assert data["action"] == "create"


@pytest.mark.anyio
async def test_chat_list_tasks():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a task first
        await client.post("/api/chat", json={"message": "Buy milk"})

        # List tasks
        response = await client.post("/api/chat", json={
            "message": "show my tasks"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "list"
    assert "Buy milk" in data["response"]


@pytest.mark.anyio
async def test_chat_complete_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create task
        await client.post("/api/chat", json={"message": "Buy milk"})

        # Complete it
        response = await client.post("/api/chat", json={
            "message": "complete Buy milk"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "complete"


@pytest.mark.anyio
async def test_chat_delete_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create task
        await client.post("/api/chat", json={"message": "Buy milk"})

        # Delete it
        response = await client.post("/api/chat", json={
            "message": "delete Buy milk"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "delete"


@pytest.mark.anyio
async def test_chat_help():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/chat", json={
            "message": "help"
        })
    assert response.status_code == 200
    data = response.json()
    assert "help" in data["response"].lower() or "task" in data["response"].lower()


@pytest.mark.anyio
async def test_chat_urdu_create():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/chat", json={
            "message": "Doodh lana hai"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "create"


@pytest.mark.anyio
async def test_chat_urdu_list():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/chat", json={"message": "Chai banana"})

        response = await client.post("/api/chat", json={
            "message": "tasks dikhao"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "list"


@pytest.mark.anyio
async def test_chat_high_priority():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/chat", json={
            "message": "urgent: Submit report"
        })
    assert response.status_code == 200
    data = response.json()
    assert "High" in data["response"] or "priority" in data["response"].lower()
