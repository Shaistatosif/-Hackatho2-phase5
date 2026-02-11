"""Tests for Pydantic models."""

from datetime import datetime
from uuid import UUID

from src.models.task import Priority, RecurrencePattern, Task, TaskStatus
from src.models.events import EventType, TaskEvent
from src.models.schemas import TaskCreateRequest, TaskUpdateRequest, TaskFilterParams


def test_task_creation():
    task = Task(user_id="user-1", title="Test task")
    assert task.title == "Test task"
    assert task.user_id == "user-1"
    assert task.status == TaskStatus.PENDING
    assert task.priority == Priority.MEDIUM
    assert isinstance(task.id, UUID)
    assert task.tags == []


def test_task_state_key():
    task = Task(user_id="user-1", title="Test")
    key = task.get_state_key()
    assert key == f"task:user-1:{task.id}"


def test_task_mark_completed():
    task = Task(user_id="user-1", title="Test")
    assert task.status == TaskStatus.PENDING
    assert task.completed_at is None

    task.mark_completed()
    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at is not None


def test_task_is_recurring():
    task = Task(user_id="user-1", title="Daily task", recurrence_pattern=RecurrencePattern.DAILY)
    assert task.is_recurring() is True

    task2 = Task(user_id="user-1", title="Normal task")
    assert task2.is_recurring() is False


def test_task_with_all_fields():
    task = Task(
        user_id="user-1",
        title="Full task",
        description="Description here",
        priority=Priority.HIGH,
        tags=["work", "urgent"],
        due_at=datetime(2026, 3, 1, 17, 0),
        remind_at=datetime(2026, 3, 1, 16, 0),
        recurrence_pattern=RecurrencePattern.WEEKLY,
    )
    assert task.priority == Priority.HIGH
    assert len(task.tags) == 2
    assert task.recurrence_pattern == RecurrencePattern.WEEKLY


def test_task_create_request_defaults():
    req = TaskCreateRequest(title="Test")
    assert req.priority == Priority.MEDIUM
    assert req.tags == []
    assert req.due_at is None


def test_task_update_request_partial():
    req = TaskUpdateRequest(title="Updated")
    data = req.model_dump(exclude_unset=True)
    assert "title" in data
    assert "priority" not in data


def test_task_filter_params_defaults():
    params = TaskFilterParams()
    assert params.page == 1
    assert params.page_size == 20
    assert params.sort_by == "created_at"
    assert params.sort_order == "desc"


def test_task_event_creation():
    task = Task(user_id="user-1", title="Test")
    event = TaskEvent.create(
        event_type=EventType.CREATED,
        task=task,
        metadata={"source_action": "test"}
    )
    assert event.type == "task.created"
    assert event.data.task_id == task.id
    assert event.data.metadata["source_action"] == "test"
    assert event.source == "backend"
