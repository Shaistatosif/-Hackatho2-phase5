# T064, T065, T066 - Recurring Task Event Handlers
# Phase V Todo Chatbot - Recurring Task Processing
"""
Handlers for processing completed task events and creating next occurrences.
"""

import os
from datetime import datetime, timedelta

import httpx
import structlog
from dateutil.relativedelta import relativedelta

logger = structlog.get_logger()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3500/v1.0/invoke/backend/method")


async def handle_task_event(event: dict) -> None:
    """
    Process a task.completed event and create next occurrence if recurring.
    """
    data = event.get("data", event)
    task_data = data.get("task_data")

    if not task_data:
        logger.warning("no_task_data_in_event")
        return

    recurrence_pattern = task_data.get("recurrence_pattern")

    if not recurrence_pattern:
        logger.debug("task_not_recurring", task_id=data.get("task_id"))
        return

    logger.info(
        "processing_recurring_task",
        task_id=data.get("task_id"),
        pattern=recurrence_pattern
    )

    # T065 - Calculate next due date
    current_due = task_data.get("due_at")
    next_due = calculate_next_due(current_due, recurrence_pattern)

    # T066 - Create next task occurrence
    await create_next_occurrence(task_data, next_due)


def calculate_next_due(current_due: str | None, pattern: str) -> datetime:
    """
    T065 - Calculate the next due date based on recurrence pattern.

    Args:
        current_due: Current due date (ISO format) or None
        pattern: One of 'daily', 'weekly', 'monthly'

    Returns:
        Next due datetime
    """
    if current_due:
        base_date = datetime.fromisoformat(current_due.replace("Z", "+00:00"))
    else:
        base_date = datetime.utcnow()

    if pattern == "daily":
        return base_date + timedelta(days=1)
    elif pattern == "weekly":
        return base_date + timedelta(weeks=1)
    elif pattern == "monthly":
        return base_date + relativedelta(months=1)
    else:
        # Default to daily if unknown pattern
        logger.warning("unknown_recurrence_pattern", pattern=pattern)
        return base_date + timedelta(days=1)


async def create_next_occurrence(task_data: dict, next_due: datetime) -> None:
    """
    T066 - Create the next task occurrence via backend API.

    Args:
        task_data: Original task data
        next_due: Calculated next due date
    """
    user_id = task_data.get("user_id")

    # Prepare new task data
    new_task = {
        "title": task_data.get("title"),
        "description": task_data.get("description"),
        "priority": task_data.get("priority", "Medium"),
        "tags": task_data.get("tags", []),
        "recurrence_pattern": task_data.get("recurrence_pattern"),
        "due_at": next_due.isoformat() + "Z"
    }

    # Calculate remind_at based on original task's reminder offset
    original_due = task_data.get("due_at")
    original_remind = task_data.get("remind_at")

    if original_due and original_remind:
        due_dt = datetime.fromisoformat(original_due.replace("Z", "+00:00"))
        remind_dt = datetime.fromisoformat(original_remind.replace("Z", "+00:00"))
        offset = due_dt - remind_dt

        new_remind = next_due - offset
        new_task["remind_at"] = new_remind.isoformat() + "Z"

    logger.info(
        "creating_next_occurrence",
        user_id=user_id,
        original_task_id=task_data.get("id"),
        new_due=new_task["due_at"]
    )

    # Call backend API via Dapr service invocation
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/tasks",
                json=new_task,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {user_id}"
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                "next_occurrence_created",
                new_task_id=result.get("id"),
                user_id=user_id
            )
        except httpx.HTTPError as e:
            logger.error(
                "failed_to_create_next_occurrence",
                error=str(e),
                user_id=user_id
            )
            raise
