# T014, T015, T088 - Event Pydantic Models
# Phase V Todo Chatbot - CloudEvents for Kafka
"""
Event models following CloudEvents 1.0 specification.
Used for Kafka message payloads via Dapr Pub/Sub.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .task import Task


class EventType(str, Enum):
    """Task event types."""
    CREATED = "task.created"
    UPDATED = "task.updated"
    COMPLETED = "task.completed"
    DELETED = "task.deleted"


class CloudEventBase(BaseModel):
    """
    CloudEvents 1.0 envelope base.
    All Kafka messages follow this format.
    """
    specversion: str = Field(default="1.0", description="CloudEvents spec version")
    id: UUID = Field(default_factory=uuid4, description="Event unique identifier")
    source: str = Field(..., description="Service that produced the event")
    type: str = Field(..., description="Event type")
    time: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    datacontenttype: str = Field(default="application/json", description="Data content type")


class TaskEventData(BaseModel):
    """Data payload for task events."""
    event_type: str = Field(..., description="Event type (created, updated, completed, deleted)")
    task_id: UUID = Field(..., description="Task identifier")
    task_data: Optional[dict[str, Any]] = Field(None, description="Full task object (null for deleted)")
    user_id: str = Field(..., description="User identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")


class TaskEvent(CloudEventBase):
    """
    T014 - Task event published to task-events topic.
    Consumed by: Audit Service, Recurring Task Service, WebSocket Service
    """
    type: str = Field(..., description="One of: task.created, task.updated, task.completed, task.deleted")
    data: TaskEventData

    @classmethod
    def create(
        cls,
        event_type: EventType,
        task: Task,
        source: str = "backend",
        metadata: Optional[dict[str, Any]] = None
    ) -> "TaskEvent":
        """Factory method to create TaskEvent from Task."""
        return cls(
            source=source,
            type=event_type.value,
            data=TaskEventData(
                event_type=event_type.value.split(".")[-1],  # created, updated, etc.
                task_id=task.id,
                task_data=task.model_dump(mode="json") if event_type != EventType.DELETED else None,
                user_id=task.user_id,
                metadata=metadata or {"source_action": "api"}
            )
        )


class ReminderEventData(BaseModel):
    """Data payload for reminder events."""
    task_id: UUID = Field(..., description="Task identifier")
    title: str = Field(..., description="Task title for notification display")
    due_at: datetime = Field(..., description="Task due date/time")
    remind_at: datetime = Field(..., description="Reminder trigger time")
    user_id: str = Field(..., description="User identifier")
    notification_channels: list[str] = Field(default=["in_app"], description="Notification channels")


class ReminderEvent(CloudEventBase):
    """
    T015 - Reminder event published to reminders topic.
    Published by: Backend (via Dapr Jobs callback)
    Consumed by: Notification Service
    """
    type: str = Field(default="reminder.due", description="Reminder event type")
    data: ReminderEventData

    @classmethod
    def create(cls, task: Task, source: str = "backend") -> "ReminderEvent":
        """Factory method to create ReminderEvent from Task."""
        if not task.due_at or not task.remind_at:
            raise ValueError("Task must have due_at and remind_at for reminder")

        return cls(
            source=source,
            data=ReminderEventData(
                task_id=task.id,
                title=task.title,
                due_at=task.due_at,
                remind_at=task.remind_at,
                user_id=task.user_id
            )
        )


class AuditAction(str, Enum):
    """Audit log action types."""
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    DELETED = "deleted"


class AuditEntry(BaseModel):
    """
    T088 - Audit log entry stored by Audit Service.
    Created from TaskEvent consumption.
    """
    id: UUID = Field(default_factory=uuid4, description="Audit entry ID")
    task_id: UUID = Field(..., description="Task identifier")
    user_id: str = Field(..., description="User identifier")
    action: AuditAction = Field(..., description="Action performed")
    task_snapshot: Optional[dict[str, Any]] = Field(None, description="Task state at time of action")
    previous_state: Optional[dict[str, Any]] = Field(None, description="Previous task state (for updates)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Action timestamp")
    source: str = Field(default="api", description="Action source (api, chat, recurring)")

    class Config:
        use_enum_values = True

    def get_state_key(self) -> str:
        """Generate Dapr state store key for this audit entry."""
        return f"audit:{self.user_id}:{self.id}"
