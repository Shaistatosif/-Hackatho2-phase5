"""Tests for Task CRUD API endpoints."""

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
async def test_create_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/tasks", json={
            "title": "Buy groceries",
            "priority": "High",
            "tags": ["shopping"]
        })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["priority"] == "High"
    assert data["status"] == "pending"
    assert "shopping" in data["tags"]
    assert data["id"] is not None


@pytest.mark.anyio
async def test_list_tasks():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create two tasks
        await client.post("/api/tasks", json={"title": "Task 1"})
        await client.post("/api/tasks", json={"title": "Task 2"})

        response = await client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["tasks"]) == 2


@pytest.mark.anyio
async def test_complete_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create task
        create_resp = await client.post("/api/tasks", json={"title": "Do homework"})
        task_id = create_resp.json()["id"]

        # Complete it
        response = await client.post(f"/api/tasks/{task_id}/complete")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


@pytest.mark.anyio
async def test_update_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create task
        create_resp = await client.post("/api/tasks", json={"title": "Old title"})
        task_id = create_resp.json()["id"]

        # Update it
        response = await client.put(f"/api/tasks/{task_id}", json={
            "title": "New title",
            "priority": "Low"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["priority"] == "Low"


@pytest.mark.anyio
async def test_delete_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create task
        create_resp = await client.post("/api/tasks", json={"title": "Delete me"})
        task_id = create_resp.json()["id"]

        # Delete it
        response = await client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 204


@pytest.mark.anyio
async def test_delete_nonexistent_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/api/tasks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_task_with_all_fields():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/tasks", json={
            "title": "Full task",
            "description": "A detailed description",
            "priority": "High",
            "tags": ["work", "urgent"],
            "due_at": "2026-03-01T17:00:00Z",
            "remind_at": "2026-03-01T16:00:00Z",
            "recurrence_pattern": "daily"
        })
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "A detailed description"
    assert data["recurrence_pattern"] == "daily"
    assert len(data["tags"]) == 2
