# T013 - Task Pydantic Model
# Phase V Todo Chatbot - Core Task Entity
"""
Task model representing a todo item with all its properties.
Follows data-model.md specification.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task completion status."""
    PENDING = "pending"
    COMPLETED = "completed"


class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class RecurrencePattern(str, Enum):
    """Supported recurrence patterns."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Task(BaseModel):
    """
    Task entity representing a todo item.

    Key patterns:
    - ID is UUID for global uniqueness
    - user_id scopes tasks to users
    - status tracks completion state
    - Dapr State Store key: task:{user_id}:{task_id}
    """
    id: UUID = Field(default_factory=uuid4, description="Unique task identifier")
    user_id: str = Field(..., description="Owner user identifier")
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Completion status")
    priority: Priority = Field(default=Priority.MEDIUM, description="Priority level")
    tags: list[str] = Field(default_factory=list, description="Task tags")
    due_at: Optional[datetime] = Field(None, description="Due date/time")
    remind_at: Optional[datetime] = Field(None, description="Reminder date/time")
    recurrence_pattern: Optional[RecurrencePattern] = Field(None, description="Recurrence pattern")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "status": "pending",
                "priority": "High",
                "tags": ["shopping", "urgent"],
                "due_at": "2026-02-10T17:00:00Z",
                "remind_at": "2026-02-10T16:00:00Z",
                "recurrence_pattern": None,
                "created_at": "2026-02-09T12:00:00Z",
                "updated_at": "2026-02-09T12:00:00Z",
                "completed_at": None
            }
        }

    def get_state_key(self) -> str:
        """Generate Dapr state store key for this task."""
        return f"task:{self.user_id}:{self.id}"

    def mark_completed(self) -> "Task":
        """Mark task as completed with timestamp."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return self

    def is_recurring(self) -> bool:
        """Check if task has recurrence pattern."""
        return self.recurrence_pattern is not None
