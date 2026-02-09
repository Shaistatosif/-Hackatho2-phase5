# T017, T018, T019 - Dapr Client Service
# Phase V Todo Chatbot - Dapr HTTP API Client
"""
DaprClient provides abstraction over Dapr HTTP APIs.
All infrastructure access (state, pubsub, jobs) goes through this client.

Constitution Principle III: No direct Kafka/DB clients - all via Dapr.
"""

import os
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

import httpx
import structlog

logger = structlog.get_logger()

# Dapr sidecar configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"

# Component names from dapr-components/
PUBSUB_NAME = "kafka-pubsub"
STATESTORE_NAME = "statestore"


class DaprClient:
    """
    Async HTTP client for Dapr sidecar APIs.

    Provides methods for:
    - T017: State Store operations (save, get, delete)
    - T018: Pub/Sub operations (publish events to Kafka)
    - T019: Jobs API operations (schedule/cancel reminders)
    """

    def __init__(self, timeout: float = 30.0):
        """Initialize Dapr client with configurable timeout."""
        self.base_url = DAPR_BASE_URL
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # =========================================================================
    # T017: State Store Operations
    # =========================================================================

    async def save_state(
        self,
        key: str,
        value: dict[str, Any],
        etag: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None
    ) -> bool:
        """
        Save state to Dapr State Store (Neon PostgreSQL).

        Args:
            key: State key (e.g., "task:user-123:uuid")
            value: JSON-serializable value
            etag: Optional ETag for concurrency control
            metadata: Optional metadata

        Returns:
            True if successful, False otherwise
        """
        client = await self._get_client()
        url = f"/v1.0/state/{STATESTORE_NAME}"

        state_item = {
            "key": key,
            "value": value
        }
        if etag:
            state_item["etag"] = etag
        if metadata:
            state_item["metadata"] = metadata

        try:
            response = await client.post(url, json=[state_item])
            response.raise_for_status()
            logger.info("state_saved", key=key)
            return True
        except httpx.HTTPStatusError as e:
            logger.error("state_save_failed", key=key, status=e.response.status_code, error=str(e))
            return False

    async def get_state(self, key: str) -> Optional[dict[str, Any]]:
        """
        Get state from Dapr State Store.

        Args:
            key: State key

        Returns:
            State value or None if not found
        """
        client = await self._get_client()
        url = f"/v1.0/state/{STATESTORE_NAME}/{key}"

        try:
            response = await client.get(url)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json() if response.text else None
        except httpx.HTTPStatusError as e:
            logger.error("state_get_failed", key=key, status=e.response.status_code, error=str(e))
            return None

    async def delete_state(self, key: str) -> bool:
        """
        Delete state from Dapr State Store.

        Args:
            key: State key

        Returns:
            True if successful (or not found), False on error
        """
        client = await self._get_client()
        url = f"/v1.0/state/{STATESTORE_NAME}/{key}"

        try:
            response = await client.delete(url)
            if response.status_code in (200, 204, 404):
                logger.info("state_deleted", key=key)
                return True
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            logger.error("state_delete_failed", key=key, status=e.response.status_code, error=str(e))
            return False

    async def query_state(
        self,
        filter_query: dict[str, Any],
        sort: Optional[list[dict[str, str]]] = None,
        page: dict[str, int] = None
    ) -> list[dict[str, Any]]:
        """
        Query state using Dapr State Query API.

        Args:
            filter_query: Query filter (MongoDB-like syntax)
            sort: Sort specification
            page: Pagination (limit, token)

        Returns:
            List of matching state items
        """
        client = await self._get_client()
        url = f"/v1.0-alpha1/state/{STATESTORE_NAME}/query"

        query = {"filter": filter_query}
        if sort:
            query["sort"] = sort
        if page:
            query["page"] = page

        try:
            response = await client.post(url, json=query)
            response.raise_for_status()
            result = response.json()
            return result.get("results", [])
        except httpx.HTTPStatusError as e:
            logger.error("state_query_failed", filter=filter_query, status=e.response.status_code, error=str(e))
            return []

    # =========================================================================
    # T018: Pub/Sub Operations (Kafka via Dapr)
    # =========================================================================

    async def publish_event(
        self,
        topic: str,
        data: dict[str, Any],
        metadata: Optional[dict[str, str]] = None
    ) -> bool:
        """
        Publish event to Kafka topic via Dapr Pub/Sub.

        Args:
            topic: Kafka topic name (task-events, reminders, task-updates)
            data: CloudEvents-formatted message data
            metadata: Optional message metadata

        Returns:
            True if published successfully, False otherwise
        """
        client = await self._get_client()
        url = f"/v1.0/publish/{PUBSUB_NAME}/{topic}"

        headers = {"Content-Type": "application/cloudevents+json"}
        if metadata:
            for key, value in metadata.items():
                headers[f"metadata.{key}"] = value

        try:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            logger.info("event_published", topic=topic, event_type=data.get("type"))
            return True
        except httpx.HTTPStatusError as e:
            logger.error("event_publish_failed", topic=topic, status=e.response.status_code, error=str(e))
            return False

    # =========================================================================
    # T019: Jobs API Operations (Reminders)
    # =========================================================================

    async def schedule_job(
        self,
        job_name: str,
        schedule_at: datetime,
        data: dict[str, Any],
        callback_url: str = "/api/jobs/reminder"
    ) -> bool:
        """
        Schedule a one-time job via Dapr Jobs API.

        Args:
            job_name: Unique job identifier (e.g., "reminder:{task_id}")
            schedule_at: When to trigger the job
            data: Job payload data
            callback_url: Callback endpoint when job fires

        Returns:
            True if scheduled successfully, False otherwise
        """
        client = await self._get_client()
        url = f"/v1.0-alpha1/jobs/{job_name}"

        # Calculate schedule in RFC3339 format
        schedule_time = schedule_at.isoformat() + "Z" if not schedule_at.tzinfo else schedule_at.isoformat()

        job_spec = {
            "schedule": f"@once {schedule_time}",
            "data": data,
            "callback": {
                "method": "POST",
                "path": callback_url
            }
        }

        try:
            response = await client.post(url, json=job_spec)
            response.raise_for_status()
            logger.info("job_scheduled", job_name=job_name, schedule_at=schedule_time)
            return True
        except httpx.HTTPStatusError as e:
            logger.error("job_schedule_failed", job_name=job_name, status=e.response.status_code, error=str(e))
            return False

    async def cancel_job(self, job_name: str) -> bool:
        """
        Cancel a scheduled job.

        Args:
            job_name: Job identifier to cancel

        Returns:
            True if cancelled successfully (or not found), False on error
        """
        client = await self._get_client()
        url = f"/v1.0-alpha1/jobs/{job_name}"

        try:
            response = await client.delete(url)
            if response.status_code in (200, 204, 404):
                logger.info("job_cancelled", job_name=job_name)
                return True
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            logger.error("job_cancel_failed", job_name=job_name, status=e.response.status_code, error=str(e))
            return False

    async def get_job(self, job_name: str) -> Optional[dict[str, Any]]:
        """
        Get job details.

        Args:
            job_name: Job identifier

        Returns:
            Job details or None if not found
        """
        client = await self._get_client()
        url = f"/v1.0-alpha1/jobs/{job_name}"

        try:
            response = await client.get(url)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error("job_get_failed", job_name=job_name, status=e.response.status_code, error=str(e))
            return None


# Global client instance for dependency injection
_dapr_client: Optional[DaprClient] = None


def get_dapr_client() -> DaprClient:
    """Get or create global DaprClient instance."""
    global _dapr_client
    if _dapr_client is None:
        _dapr_client = DaprClient()
    return _dapr_client
