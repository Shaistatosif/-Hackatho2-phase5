# T016 - Request/Response Schemas
# Phase V Todo Chatbot - API Schemas
"""
Request and response schemas for API endpoints.
Separate from domain models for API contract stability.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .task import Priority, RecurrencePattern, TaskStatus


# =============================================================================
# Chat API Schemas
# =============================================================================

class ChatRequest(BaseModel):
    """Request body for POST /api/chat."""
    message: str = Field(..., min_length=1, max_length=1000, description="Natural language message")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Add task: Buy groceries with high priority, due tomorrow at 5pm"
            }
        }


class ChatResponse(BaseModel):
    """Response body for POST /api/chat."""
    response: str = Field(..., description="Assistant response message")
    task_id: Optional[UUID] = Field(None, description="Created/modified task ID if applicable")
    action: Optional[str] = Field(None, description="Action performed (create, update, complete, delete, list)")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "I've created a task 'Buy groceries' with high priority, due tomorrow at 5pm.",
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "action": "create"
            }
        }


# =============================================================================
# Task API Schemas
# =============================================================================

class TaskCreateRequest(BaseModel):
    """Request body for POST /api/tasks."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Priority = Field(default=Priority.MEDIUM)
    tags: list[str] = Field(default_factory=list)
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePattern] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "priority": "High",
                "tags": ["shopping"],
                "due_at": "2026-02-10T17:00:00Z",
                "remind_at": "2026-02-10T16:00:00Z"
            }
        }


class TaskUpdateRequest(BaseModel):
    """Request body for PUT /api/tasks/{id}."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[Priority] = None
    tags: Optional[list[str]] = None
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    status: Optional[TaskStatus] = None

    class Config:
        json_schema_extra = {
            "example": {
                "priority": "Low",
                "due_at": "2026-02-11T17:00:00Z"
            }
        }


class TaskResponse(BaseModel):
    """Response body for task endpoints."""
    id: UUID
    user_id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: Priority
    tags: list[str]
    due_at: Optional[datetime]
    remind_at: Optional[datetime]
    recurrence_pattern: Optional[RecurrencePattern]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Response body for GET /api/tasks."""
    tasks: list[TaskResponse]
    total: int = Field(..., description="Total number of tasks matching filters")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=20, description="Items per page")


# =============================================================================
# Audit API Schemas
# =============================================================================

class AuditEntryResponse(BaseModel):
    """Single audit log entry response."""
    id: UUID
    task_id: UUID
    action: str
    timestamp: datetime
    source: str
    task_snapshot: Optional[dict] = None


class AuditLogResponse(BaseModel):
    """Response body for GET /api/audit."""
    entries: list[AuditEntryResponse]
    total: int


# =============================================================================
# Filter/Sort Schemas
# =============================================================================

class TaskFilterParams(BaseModel):
    """Query parameters for task filtering."""
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    tags: Optional[list[str]] = None
    due_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    search: Optional[str] = Field(None, description="Full-text search query")
    sort_by: Optional[str] = Field("created_at", description="Sort field: created_at, due_at, priority")
    sort_order: Optional[str] = Field("desc", description="Sort order: asc, desc")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
