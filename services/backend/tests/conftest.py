"""Shared test fixtures for backend tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.services.memory_store import MemoryStore, _store


@pytest.fixture(autouse=True)
def clear_store():
    """Clear in-memory store before each test."""
    _store.clear()
    yield
    _store.clear()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Async test client for FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
