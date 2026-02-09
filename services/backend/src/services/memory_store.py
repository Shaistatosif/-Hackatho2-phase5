# In-Memory Store - Replaces Dapr for standalone deployment
"""
Simple in-memory storage for Vercel/HuggingFace deployment.
Replaces Dapr State Store, Pub/Sub, and Jobs APIs.
"""

from typing import Any, Optional
import structlog

logger = structlog.get_logger()

# In-memory storage
_store: dict[str, Any] = {}
_audit_log: list[dict[str, Any]] = []


class MemoryStore:
    """In-memory key-value store replacing Dapr State Store."""

    async def save_state(self, key: str, value: dict[str, Any], **kwargs) -> bool:
        _store[key] = value
        logger.info("state_saved", key=key)
        return True

    async def get_state(self, key: str) -> Optional[dict[str, Any]]:
        return _store.get(key)

    async def delete_state(self, key: str) -> bool:
        _store.pop(key, None)
        logger.info("state_deleted", key=key)
        return True

    async def query_state(self, filter_query: dict, sort=None, page=None) -> list[dict]:
        """Simple filter over in-memory store."""
        results = []
        for key, value in _store.items():
            if key.startswith("task:"):
                results.append({"key": key, "data": value})
        return results

    async def publish_event(self, topic: str, data: dict, **kwargs) -> bool:
        """No-op for standalone mode. Just log."""
        logger.info("event_published_noop", topic=topic, event_type=data.get("type"))
        if topic == "task-events":
            _audit_log.append(data)
        return True

    async def schedule_job(self, job_name: str, schedule_at=None, data=None, **kwargs) -> bool:
        logger.info("job_scheduled_noop", job_name=job_name)
        return True

    async def cancel_job(self, job_name: str) -> bool:
        logger.info("job_cancelled_noop", job_name=job_name)
        return True

    async def close(self):
        pass


_memory_store: Optional[MemoryStore] = None


def get_memory_store() -> MemoryStore:
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
    return _memory_store


def get_audit_log() -> list[dict]:
    return _audit_log
