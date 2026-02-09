# T029-T035, T050-T052, T060, T067-T069, T074-T076, T082 - Task Service
# Phase V Todo Chatbot - Task Business Logic
"""
TaskService handles all task operations with Dapr integration.
Each operation saves state and publishes events to Kafka.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

import structlog

from ..models.task import Priority, RecurrencePattern, Task, TaskStatus
from ..models.events import EventType, TaskEvent
from ..models.schemas import TaskCreateRequest, TaskUpdateRequest, TaskFilterParams
from .memory_store import MemoryStore, get_memory_store

logger = structlog.get_logger()

# Kafka topics
TOPIC_TASK_EVENTS = "task-events"
TOPIC_TASK_UPDATES = "task-updates"


class TaskService:
    """
    Service for task CRUD operations.
    All operations:
    1. Validate input
    2. Perform operation via Dapr State Store
    3. Publish event to Kafka via Dapr Pub/Sub
    """

    def __init__(self, store: Optional[MemoryStore] = None):
        """Initialize with optional store for testing."""
        self.dapr = store or get_memory_store()

    # =========================================================================
    # T029 - Create Task
    # =========================================================================

    async def create_task(
        self,
        user_id: str,
        request: TaskCreateRequest,
        source: str = "api"
    ) -> Task:
        """
        Create a new task.

        Args:
            user_id: Owner user ID
            request: Task creation request
            source: Action source (api, chat, recurring)

        Returns:
            Created Task
        """
        # Create task entity
        task = Task(
            user_id=user_id,
            title=request.title,
            description=request.description,
            priority=request.priority,
            tags=request.tags,
            due_at=request.due_at,
            remind_at=request.remind_at,
            recurrence_pattern=request.recurrence_pattern
        )

        # Save to Dapr State Store
        success = await self.dapr.save_state(
            key=task.get_state_key(),
            value=task.model_dump(mode="json")
        )

        if not success:
            raise RuntimeError(f"Failed to save task {task.id}")

        # T035 - Publish task.created event
        event = TaskEvent.create(
            event_type=EventType.CREATED,
            task=task,
            metadata={"source_action": source}
        )
        await self.dapr.publish_event(TOPIC_TASK_EVENTS, event.model_dump(mode="json"))

        # T082 - Publish to task-updates for real-time sync
        await self.dapr.publish_event(TOPIC_TASK_UPDATES, event.model_dump(mode="json"))

        # T051 - Schedule reminder if remind_at is set
        if task.remind_at:
            await self._schedule_reminder(task)

        logger.info("task_created", task_id=str(task.id), user_id=user_id, source=source)
        return task

    # =========================================================================
    # T030 - Get Task
    # =========================================================================

    async def get_task(self, user_id: str, task_id: UUID) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            user_id: Owner user ID (for authorization)
            task_id: Task ID

        Returns:
            Task or None if not found
        """
        key = f"task:{user_id}:{task_id}"
        data = await self.dapr.get_state(key)

        if not data:
            return None

        return Task.model_validate(data)

    # =========================================================================
    # T031 - Update Task
    # =========================================================================

    async def update_task(
        self,
        user_id: str,
        task_id: UUID,
        request: TaskUpdateRequest,
        source: str = "api"
    ) -> Optional[Task]:
        """
        Update an existing task.

        Args:
            user_id: Owner user ID
            task_id: Task ID
            request: Update request with fields to change
            source: Action source

        Returns:
            Updated Task or None if not found
        """
        # Get existing task
        task = await self.get_task(user_id, task_id)
        if not task:
            return None

        # Store previous state for audit
        previous_state = task.model_dump(mode="json")

        # Apply updates
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(task, field, value)

        task.updated_at = datetime.utcnow()

        # Save updated task
        success = await self.dapr.save_state(
            key=task.get_state_key(),
            value=task.model_dump(mode="json")
        )

        if not success:
            raise RuntimeError(f"Failed to update task {task_id}")

        # T035 - Publish task.updated event
        event = TaskEvent.create(
            event_type=EventType.UPDATED,
            task=task,
            metadata={"source_action": source, "previous_state": previous_state}
        )
        await self.dapr.publish_event(TOPIC_TASK_EVENTS, event.model_dump(mode="json"))
        await self.dapr.publish_event(TOPIC_TASK_UPDATES, event.model_dump(mode="json"))

        # T050, T052 - Handle reminder updates
        if "remind_at" in update_data or "due_at" in update_data:
            # Cancel existing reminder
            await self._cancel_reminder(task)
            # Schedule new reminder if set
            if task.remind_at:
                await self._schedule_reminder(task)

        logger.info("task_updated", task_id=str(task_id), user_id=user_id, source=source)
        return task

    # =========================================================================
    # T032 - Delete Task
    # =========================================================================

    async def delete_task(
        self,
        user_id: str,
        task_id: UUID,
        source: str = "api"
    ) -> bool:
        """
        Delete a task.

        Args:
            user_id: Owner user ID
            task_id: Task ID
            source: Action source

        Returns:
            True if deleted, False if not found
        """
        # Get task for event
        task = await self.get_task(user_id, task_id)
        if not task:
            return False

        # Delete from state store
        key = f"task:{user_id}:{task_id}"
        success = await self.dapr.delete_state(key)

        if not success:
            raise RuntimeError(f"Failed to delete task {task_id}")

        # T035 - Publish task.deleted event
        event = TaskEvent.create(
            event_type=EventType.DELETED,
            task=task,
            metadata={"source_action": source}
        )
        await self.dapr.publish_event(TOPIC_TASK_EVENTS, event.model_dump(mode="json"))
        await self.dapr.publish_event(TOPIC_TASK_UPDATES, event.model_dump(mode="json"))

        # T052 - Cancel any scheduled reminder
        await self._cancel_reminder(task)

        logger.info("task_deleted", task_id=str(task_id), user_id=user_id, source=source)
        return True

    # =========================================================================
    # T033 - Complete Task
    # =========================================================================

    async def complete_task(
        self,
        user_id: str,
        task_id: UUID,
        source: str = "api"
    ) -> Optional[Task]:
        """
        Mark a task as completed.

        Args:
            user_id: Owner user ID
            task_id: Task ID
            source: Action source

        Returns:
            Completed Task or None if not found
        """
        task = await self.get_task(user_id, task_id)
        if not task:
            return None

        # Mark completed
        task.mark_completed()

        # Save updated task
        success = await self.dapr.save_state(
            key=task.get_state_key(),
            value=task.model_dump(mode="json")
        )

        if not success:
            raise RuntimeError(f"Failed to complete task {task_id}")

        # T035 - Publish task.completed event
        # This triggers recurring task service to create next occurrence
        event = TaskEvent.create(
            event_type=EventType.COMPLETED,
            task=task,
            metadata={"source_action": source}
        )
        await self.dapr.publish_event(TOPIC_TASK_EVENTS, event.model_dump(mode="json"))
        await self.dapr.publish_event(TOPIC_TASK_UPDATES, event.model_dump(mode="json"))

        # T052 - Cancel reminder on completion
        await self._cancel_reminder(task)

        logger.info("task_completed", task_id=str(task_id), user_id=user_id, source=source)
        return task

    # =========================================================================
    # T034 - List Tasks
    # =========================================================================

    async def list_tasks(
        self,
        user_id: str,
        filters: Optional[TaskFilterParams] = None
    ) -> tuple[list[Task], int]:
        """
        List tasks for a user with optional filtering.

        Args:
            user_id: Owner user ID
            filters: Optional filter/sort/pagination parameters

        Returns:
            Tuple of (tasks list, total count)
        """
        filters = filters or TaskFilterParams()

        # Build query filter
        query_filter = {
            "AND": [
                {"EQ": {"user_id": user_id}}
            ]
        }

        # T068 - Apply filters
        if filters.status:
            query_filter["AND"].append({"EQ": {"status": filters.status}})
        if filters.priority:
            query_filter["AND"].append({"EQ": {"priority": filters.priority}})
        if filters.due_before:
            query_filter["AND"].append({"LT": {"due_at": filters.due_before.isoformat()}})
        if filters.due_after:
            query_filter["AND"].append({"GT": {"due_at": filters.due_after.isoformat()}})

        # T069 - Apply sort
        sort = []
        if filters.sort_by:
            sort.append({
                "key": filters.sort_by,
                "order": filters.sort_order.upper() if filters.sort_order else "DESC"
            })

        # Query state store
        results = await self.dapr.query_state(
            filter_query=query_filter,
            sort=sort if sort else None,
            page={"limit": filters.page_size}
        )

        # Parse results
        tasks = []
        for result in results:
            if result.get("data"):
                task = Task.model_validate(result["data"])
                # T067 - Apply text search filter (client-side for now)
                if filters.search:
                    search_lower = filters.search.lower()
                    if search_lower not in task.title.lower() and \
                       (not task.description or search_lower not in task.description.lower()):
                        continue
                # T076 - Apply tag filter
                if filters.tags:
                    if not any(tag in task.tags for tag in filters.tags):
                        continue
                tasks.append(task)

        # Pagination
        total = len(tasks)
        start = (filters.page - 1) * filters.page_size
        end = start + filters.page_size
        paginated_tasks = tasks[start:end]

        return paginated_tasks, total

    # =========================================================================
    # T067 - Search Tasks
    # =========================================================================

    async def search_tasks(
        self,
        user_id: str,
        query: str,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[list[Task], int]:
        """
        Full-text search across task title and description.

        Args:
            user_id: Owner user ID
            query: Search query string
            page: Page number
            page_size: Items per page

        Returns:
            Tuple of (matching tasks, total count)
        """
        filters = TaskFilterParams(
            search=query,
            page=page,
            page_size=page_size
        )
        return await self.list_tasks(user_id, filters)

    # =========================================================================
    # T074 - Add Tags
    # =========================================================================

    async def add_tags(
        self,
        user_id: str,
        task_id: UUID,
        tags: list[str],
        source: str = "api"
    ) -> Optional[Task]:
        """
        Add tags to a task.

        Args:
            user_id: Owner user ID
            task_id: Task ID
            tags: Tags to add
            source: Action source

        Returns:
            Updated Task or None if not found
        """
        task = await self.get_task(user_id, task_id)
        if not task:
            return None

        # Add unique tags
        existing_tags = set(task.tags)
        new_tags = existing_tags.union(set(tags))
        task.tags = list(new_tags)
        task.updated_at = datetime.utcnow()

        # Save and publish
        await self.dapr.save_state(task.get_state_key(), task.model_dump(mode="json"))

        event = TaskEvent.create(EventType.UPDATED, task, metadata={"source_action": source})
        await self.dapr.publish_event(TOPIC_TASK_EVENTS, event.model_dump(mode="json"))
        await self.dapr.publish_event(TOPIC_TASK_UPDATES, event.model_dump(mode="json"))

        logger.info("tags_added", task_id=str(task_id), tags=tags)
        return task

    # =========================================================================
    # T075 - Remove Tags
    # =========================================================================

    async def remove_tags(
        self,
        user_id: str,
        task_id: UUID,
        tags: list[str],
        source: str = "api"
    ) -> Optional[Task]:
        """
        Remove tags from a task.

        Args:
            user_id: Owner user ID
            task_id: Task ID
            tags: Tags to remove
            source: Action source

        Returns:
            Updated Task or None if not found
        """
        task = await self.get_task(user_id, task_id)
        if not task:
            return None

        # Remove tags
        task.tags = [t for t in task.tags if t not in tags]
        task.updated_at = datetime.utcnow()

        # Save and publish
        await self.dapr.save_state(task.get_state_key(), task.model_dump(mode="json"))

        event = TaskEvent.create(EventType.UPDATED, task, metadata={"source_action": source})
        await self.dapr.publish_event(TOPIC_TASK_EVENTS, event.model_dump(mode="json"))
        await self.dapr.publish_event(TOPIC_TASK_UPDATES, event.model_dump(mode="json"))

        logger.info("tags_removed", task_id=str(task_id), tags=tags)
        return task

    # =========================================================================
    # T051 - Schedule Reminder (US2)
    # =========================================================================

    async def _schedule_reminder(self, task: Task) -> bool:
        """Schedule a reminder job for a task."""
        if not task.remind_at:
            return False

        job_name = f"reminder:{task.user_id}:{task.id}"
        job_data = {
            "task_id": str(task.id),
            "user_id": task.user_id,
            "title": task.title,
            "due_at": task.due_at.isoformat() if task.due_at else None,
            "remind_at": task.remind_at.isoformat()
        }

        return await self.dapr.schedule_job(
            job_name=job_name,
            schedule_at=task.remind_at,
            data=job_data
        )

    # =========================================================================
    # T052 - Cancel Reminder (US2)
    # =========================================================================

    async def _cancel_reminder(self, task: Task) -> bool:
        """Cancel any scheduled reminder for a task."""
        job_name = f"reminder:{task.user_id}:{task.id}"
        return await self.dapr.cancel_job(job_name)


# Global service instance for dependency injection
_task_service: Optional[TaskService] = None


def get_task_service() -> TaskService:
    """Get or create global TaskService instance."""
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service
