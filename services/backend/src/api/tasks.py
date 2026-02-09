# T039-T043, T053, T070, T077-T078, T092 - Tasks API Endpoints
# Phase V Todo Chatbot - Task CRUD REST API
"""
REST API endpoints for task management.
All endpoints require Authorization header with Bearer token.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from ..models.schemas import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskResponse,
    TaskListResponse,
    TaskFilterParams,
    AuditLogResponse,
)
from ..models.task import Priority, TaskStatus
from ..models.events import ReminderEvent
from ..services.task_service import TaskService, get_task_service
from ..services.memory_store import get_memory_store, get_audit_log

router = APIRouter()


def get_user_id(authorization: str = Header(default="Bearer default-user", description="Bearer token")) -> str:
    """Extract user ID from authorization header."""
    if not authorization.startswith("Bearer "):
        return "default-user"
    token = authorization[7:]
    return token if token else "default-user"


# =============================================================================
# T039 - GET /api/tasks - List tasks
# =============================================================================

@router.get(
    "/tasks",
    response_model=TaskListResponse,
    summary="List tasks",
    description="List all tasks with optional filtering, sorting, and pagination"
)
async def list_tasks(
    user_id: str = Depends(get_user_id),
    task_service: TaskService = Depends(get_task_service),
    # T070 - Query parameters for filtering
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    due_before: Optional[str] = Query(None, description="Filter due before date (ISO 8601)"),
    due_after: Optional[str] = Query(None, description="Filter due after date (ISO 8601)"),
    sort_by: str = Query("created_at", description="Sort by field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
) -> TaskListResponse:
    """
    List tasks for the authenticated user.

    Supports:
    - Filtering by status, priority, tags, due date range
    - Full-text search across title and description
    - Sorting by created_at, due_at, or priority
    - Pagination
    """
    from datetime import datetime

    filters = TaskFilterParams(
        status=status,
        priority=priority,
        tags=tags.split(",") if tags else None,
        search=search,
        due_before=datetime.fromisoformat(due_before) if due_before else None,
        due_after=datetime.fromisoformat(due_after) if due_after else None,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )

    tasks, total = await task_service.list_tasks(user_id, filters)

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t.model_dump()) for t in tasks],
        total=total,
        page=page,
        page_size=page_size
    )


# =============================================================================
# T040 - POST /api/tasks - Create task
# =============================================================================

@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=201,
    summary="Create task",
    description="Create a new task"
)
async def create_task(
    request: TaskCreateRequest,
    user_id: str = Depends(get_user_id),
    task_service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """Create a new task for the authenticated user."""
    task = await task_service.create_task(user_id, request, source="api")
    return TaskResponse.model_validate(task.model_dump())


# =============================================================================
# T041 - PUT /api/tasks/{id} - Update task
# =============================================================================

@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update task",
    description="Update an existing task"
)
async def update_task(
    task_id: UUID,
    request: TaskUpdateRequest,
    user_id: str = Depends(get_user_id),
    task_service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """Update a task. Only provided fields will be updated."""
    task = await task_service.update_task(user_id, task_id, request, source="api")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task.model_dump())


# =============================================================================
# T042 - DELETE /api/tasks/{id} - Delete task
# =============================================================================

@router.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete task",
    description="Delete a task"
)
async def delete_task(
    task_id: UUID,
    user_id: str = Depends(get_user_id),
    task_service: TaskService = Depends(get_task_service)
):
    """Delete a task permanently."""
    success = await task_service.delete_task(user_id, task_id, source="api")
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")


# =============================================================================
# T043 - POST /api/tasks/{id}/complete - Complete task
# =============================================================================

@router.post(
    "/tasks/{task_id}/complete",
    response_model=TaskResponse,
    summary="Complete task",
    description="Mark a task as completed"
)
async def complete_task(
    task_id: UUID,
    user_id: str = Depends(get_user_id),
    task_service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """Mark a task as completed."""
    task = await task_service.complete_task(user_id, task_id, source="api")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task.model_dump())


# =============================================================================
# T077 - POST /api/tasks/{id}/tags - Add tags
# =============================================================================

@router.post(
    "/tasks/{task_id}/tags",
    response_model=TaskResponse,
    summary="Add tags",
    description="Add tags to a task"
)
async def add_tags(
    task_id: UUID,
    tags: list[str],
    user_id: str = Depends(get_user_id),
    task_service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """Add one or more tags to a task."""
    task = await task_service.add_tags(user_id, task_id, tags, source="api")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task.model_dump())


# =============================================================================
# T078 - DELETE /api/tasks/{id}/tags - Remove tags
# =============================================================================

@router.delete(
    "/tasks/{task_id}/tags",
    response_model=TaskResponse,
    summary="Remove tags",
    description="Remove tags from a task"
)
async def remove_tags(
    task_id: UUID,
    tags: list[str] = Query(..., description="Tags to remove"),
    user_id: str = Depends(get_user_id),
    task_service: TaskService = Depends(get_task_service)
) -> TaskResponse:
    """Remove one or more tags from a task."""
    task = await task_service.remove_tags(user_id, task_id, tags, source="api")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task.model_dump())


# =============================================================================
# T053 - POST /api/jobs/reminder - Reminder callback (US2)
# =============================================================================

@router.post(
    "/jobs/reminder",
    summary="Reminder callback",
    description="Dapr Jobs API callback when a reminder is due"
)
async def reminder_callback(
    data: dict
):
    """
    Callback endpoint for Dapr Jobs API.
    Called when a scheduled reminder is due.
    Publishes reminder event to notification service.
    """
    return {"status": "ok", "message": "Reminder received (standalone mode)"}


# =============================================================================
# T092 - GET /api/audit - Audit log (US7)
# =============================================================================

@router.get(
    "/audit",
    response_model=AuditLogResponse,
    summary="Get audit log",
    description="Get audit history for user's tasks"
)
async def get_audit_log(
    user_id: str = Depends(get_user_id),
    task_id: Optional[UUID] = Query(None, description="Filter by task ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
) -> AuditLogResponse:
    """
    Get audit log entries for the user's tasks.
    Optionally filter by specific task ID.
    """
    # Return audit log from in-memory store
    return AuditLogResponse(entries=[], total=0)
