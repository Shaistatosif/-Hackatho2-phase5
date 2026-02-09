# T090, T091 - Audit Event Handlers
# Phase V Todo Chatbot - Audit Log Processing
"""
Handlers for processing task events and persisting audit entries.
"""

import os
from datetime import datetime
from uuid import uuid4

import httpx
import structlog

logger = structlog.get_logger()

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
STATESTORE_NAME = "statestore"


async def handle_task_event(event: dict) -> None:
    """
    T090 - Process a task event and store audit entry.
    """
    event_type = event.get("type", "unknown")
    data = event.get("data", event)

    task_id = data.get("task_id")
    user_id = data.get("user_id")
    task_data = data.get("task_data")
    metadata = data.get("metadata", {})

    # Create audit entry
    audit_entry = {
        "id": str(uuid4()),
        "task_id": str(task_id),
        "user_id": user_id,
        "action": event_type.split(".")[-1] if "." in event_type else event_type,
        "task_snapshot": task_data,
        "previous_state": metadata.get("previous_state"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": metadata.get("source_action", "unknown"),
        "event_id": str(event.get("id", uuid4()))
    }

    logger.info(
        "creating_audit_entry",
        audit_id=audit_entry["id"],
        task_id=task_id,
        action=audit_entry["action"]
    )

    # Save to Dapr state store
    await save_audit_entry(audit_entry)


async def save_audit_entry(entry: dict) -> bool:
    """
    Save audit entry to Dapr state store.
    """
    key = f"audit:{entry['user_id']}:{entry['id']}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{DAPR_BASE_URL}/v1.0/state/{STATESTORE_NAME}",
                json=[{
                    "key": key,
                    "value": entry
                }]
            )
            response.raise_for_status()
            logger.info("audit_entry_saved", key=key)
            return True
        except httpx.HTTPError as e:
            logger.error("audit_save_failed", key=key, error=str(e))
            return False


async def get_audit_log(user_id: str, task_id: str = None) -> list[dict]:
    """
    T091 - Get audit log entries for a user.

    Args:
        user_id: User ID
        task_id: Optional task ID to filter by

    Returns:
        List of audit entries
    """
    # Build query filter
    query_filter = {"EQ": {"user_id": user_id}}
    if task_id:
        query_filter = {
            "AND": [
                {"EQ": {"user_id": user_id}},
                {"EQ": {"task_id": task_id}}
            ]
        }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{DAPR_BASE_URL}/v1.0-alpha1/state/{STATESTORE_NAME}/query",
                json={
                    "filter": query_filter,
                    "sort": [{"key": "timestamp", "order": "DESC"}],
                    "page": {"limit": 100}
                }
            )
            response.raise_for_status()
            result = response.json()

            entries = []
            for item in result.get("results", []):
                if item.get("data"):
                    entries.append(item["data"])

            return entries
        except httpx.HTTPError as e:
            logger.error("audit_query_failed", user_id=user_id, error=str(e))
            return []
