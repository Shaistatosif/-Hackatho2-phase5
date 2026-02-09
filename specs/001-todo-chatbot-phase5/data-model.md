# Data Model: Phase V Todo Chatbot

**Date**: 2026-02-09
**Branch**: `001-todo-chatbot-phase5`

---

## Entities

### 1. Task

The primary entity representing a todo item.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string (UUID) | Yes | Auto-generated | Unique identifier |
| `user_id` | string | Yes | - | Owner of the task |
| `title` | string | Yes | - | Task title (1-200 chars) |
| `description` | string | No | null | Extended description |
| `status` | enum | Yes | "pending" | pending, completed |
| `priority` | enum | Yes | "Medium" | High, Medium, Low |
| `tags` | array[string] | No | [] | List of tag names |
| `due_at` | datetime | No | null | Due date/time (UTC) |
| `remind_at` | datetime | No | null | Reminder time (UTC) |
| `recurrence_pattern` | enum | No | null | daily, weekly, monthly |
| `recurrence_end` | datetime | No | null | When recurrence ends |
| `created_at` | datetime | Yes | Auto | Creation timestamp |
| `updated_at` | datetime | Yes | Auto | Last update timestamp |
| `completed_at` | datetime | No | null | Completion timestamp |

**State Transitions**:
```
pending → completed (via complete action)
```

**Validation Rules**:
- `title` must be 1-200 characters
- `due_at` must be in the future when set
- `remind_at` must be before `due_at` if both set
- `recurrence_pattern` valid values: daily, weekly, monthly

---

### 2. TaskEvent

Event published to Kafka for all task operations.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string (UUID) | Yes | Event unique identifier |
| `specversion` | string | Yes | CloudEvents version ("1.0") |
| `type` | enum | Yes | task.created, task.updated, task.completed, task.deleted |
| `source` | string | Yes | Service that produced event |
| `time` | datetime | Yes | Event timestamp (ISO 8601 UTC) |
| `data` | object | Yes | Event payload (see below) |

**Event Data Payload**:
```json
{
  "event_type": "created",
  "task_id": "uuid",
  "task_data": { /* full Task object */ },
  "user_id": "user-123",
  "timestamp": "2026-02-09T12:00:00Z",
  "metadata": {
    "source_action": "chat",
    "client_ip": "..."
  }
}
```

---

### 3. ReminderEvent

Event published when a reminder is due.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string (UUID) | Yes | Event unique identifier |
| `type` | string | Yes | "reminder.due" |
| `task_id` | string | Yes | Associated task ID |
| `title` | string | Yes | Task title for notification |
| `due_at` | datetime | Yes | Task due date |
| `remind_at` | datetime | Yes | When reminder was scheduled |
| `user_id` | string | Yes | User to notify |
| `notification_channels` | array[string] | Yes | ["in_app"] |

---

### 4. AuditEntry

Stored record of task operations.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string (UUID) | Yes | Audit entry ID |
| `task_id` | string | Yes | Related task ID |
| `user_id` | string | Yes | User who performed action |
| `action` | enum | Yes | created, updated, completed, deleted |
| `changes` | object | No | Field changes (for updates) |
| `timestamp` | datetime | Yes | When action occurred |
| `metadata` | object | No | Additional context |

---

### 5. User (Simplified)

User identity for multi-tenancy.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | Yes | Unique user identifier |
| `name` | string | No | Display name |
| `email` | string | No | Email for notifications |

**Note**: Full user management out of scope. Users identified by API key/JWT.

---

## Relationships

```
User (1) ────────< (N) Task
  │
  └──────────────< (N) AuditEntry

Task (1) ────────< (N) TaskEvent
  │
  └──────────────< (N) ReminderEvent (0-1 active at a time)
```

---

## State Store Keys (Dapr)

| Key Pattern | Value | Purpose |
|-------------|-------|---------|
| `task-{task_id}` | Task JSON | Individual task storage |
| `user-tasks-{user_id}` | Array of task_ids | Index for user's tasks |
| `audit-{audit_id}` | AuditEntry JSON | Audit log entry |
| `tag-index-{user_id}-{tag}` | Array of task_ids | Tag-based index |

---

## Kafka Topic Schemas

### task-events Topic
```json
{
  "specversion": "1.0",
  "type": "task.created | task.updated | task.completed | task.deleted",
  "source": "backend",
  "id": "event-uuid",
  "time": "2026-02-09T12:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "event_type": "created",
    "task_id": "task-uuid",
    "task_data": { /* Task */ },
    "user_id": "user-123",
    "timestamp": "2026-02-09T12:00:00Z"
  }
}
```

### reminders Topic
```json
{
  "specversion": "1.0",
  "type": "reminder.due",
  "source": "backend",
  "id": "event-uuid",
  "time": "2026-02-09T12:00:00Z",
  "data": {
    "task_id": "task-uuid",
    "title": "Buy groceries",
    "due_at": "2026-02-09T17:00:00Z",
    "remind_at": "2026-02-09T16:00:00Z",
    "user_id": "user-123",
    "notification_channels": ["in_app"]
  }
}
```

### task-updates Topic
```json
{
  "specversion": "1.0",
  "type": "task.changed",
  "source": "backend",
  "id": "event-uuid",
  "time": "2026-02-09T12:00:00Z",
  "data": {
    "action": "created | updated | completed | deleted",
    "task_id": "task-uuid",
    "task_data": { /* Task or null for deleted */ },
    "user_id": "user-123"
  }
}
```

---

## Indexes & Queries

### Required Query Patterns

| Query | Implementation |
|-------|----------------|
| Get all tasks for user | Dapr state query by `user_id` |
| Filter by status | Query filter: `{"EQ": {"status": "pending"}}` |
| Filter by priority | Query filter: `{"EQ": {"priority": "High"}}` |
| Filter by tag | Query filter: `{"IN": {"tags": ["work"]}}` |
| Filter by due date range | Query filter: `{"AND": [{"GTE": {"due_at": "..."}}, {"LTE": {"due_at": "..."}}]}` |
| Full-text search | Query filter with `LIKE` or application-level filter |
| Sort by field | Query with `{"sort": [{"key": "due_at", "order": "ASC"}]}` |

### Dapr State Query Example
```python
query = {
    "filter": {
        "AND": [
            {"EQ": {"user_id": "user-123"}},
            {"EQ": {"status": "pending"}},
            {"EQ": {"priority": "High"}}
        ]
    },
    "sort": [
        {"key": "due_at", "order": "ASC"}
    ],
    "page": {
        "limit": 50
    }
}
```

---

## Pydantic Models (Python)

```python
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class Status(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: Status = Status.PENDING
    priority: Priority = Priority.MEDIUM
    tags: list[str] = Field(default_factory=list)
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_end: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class EventType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    DELETED = "deleted"

class TaskEvent(BaseModel):
    event_type: EventType
    task_id: str
    task_data: dict
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = None

class ReminderEvent(BaseModel):
    task_id: str
    title: str
    due_at: datetime
    remind_at: datetime
    user_id: str
    notification_channels: list[str] = ["in_app"]
```
