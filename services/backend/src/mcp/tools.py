# T036, T055, T061, T072, T080 - MCP Tool Definitions
# Phase V Todo Chatbot - MCP Tools for LLM Function Calling
"""
MCP tool definitions for task operations.
These tools are exposed to the LLM for natural language command processing.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from ..models.task import Priority, RecurrencePattern
from ..models.schemas import TaskCreateRequest, TaskUpdateRequest, TaskFilterParams
from ..services.task_service import TaskService, get_task_service


class MCPTools:
    """
    MCP Tool definitions for task management.
    Each tool maps to a TaskService operation.
    """

    def __init__(self, task_service: Optional[TaskService] = None):
        """Initialize with optional task service for testing."""
        self.task_service = task_service or get_task_service()

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """
        Get OpenAI-compatible function definitions for all tools.
        Used for LLM function calling.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task. Use this when the user wants to add, create, or make a new task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The task title/name"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional detailed description of the task"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["High", "Medium", "Low"],
                                "description": "Task priority level. Default is Medium."
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional list of tags/categories"
                            },
                            "due_at": {
                                "type": "string",
                                "description": "Due date/time in ISO 8601 format (e.g., 2026-02-10T17:00:00Z)"
                            },
                            "remind_at": {
                                "type": "string",
                                "description": "Reminder date/time in ISO 8601 format"
                            },
                            "recurrence_pattern": {
                                "type": "string",
                                "enum": ["daily", "weekly", "monthly"],
                                "description": "Optional recurrence pattern for repeating tasks"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task. Use this when the user wants to change, modify, or edit a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title"
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["High", "Medium", "Low"],
                                "description": "New priority level"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "New list of tags (replaces existing)"
                            },
                            "due_at": {
                                "type": "string",
                                "description": "New due date/time"
                            },
                            "remind_at": {
                                "type": "string",
                                "description": "New reminder date/time"
                            },
                            "recurrence_pattern": {
                                "type": "string",
                                "enum": ["daily", "weekly", "monthly"],
                                "description": "New recurrence pattern"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed. Use this when the user says they finished, completed, or done with a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task to complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task. Use this when the user wants to remove or delete a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List all tasks or filter by criteria. Use this when the user wants to see, show, or view their tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["pending", "completed"],
                                "description": "Filter by task status"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["High", "Medium", "Low"],
                                "description": "Filter by priority"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by tags (any match)"
                            },
                            "search": {
                                "type": "string",
                                "description": "Search text in title and description"
                            },
                            "sort_by": {
                                "type": "string",
                                "enum": ["created_at", "due_at", "priority"],
                                "description": "Sort field"
                            },
                            "sort_order": {
                                "type": "string",
                                "enum": ["asc", "desc"],
                                "description": "Sort order"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_tasks",
                    "description": "Search for tasks by text. Use this when the user wants to find or search for specific tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query text"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_tags",
                    "description": "Add tags to a task. Use this when the user wants to tag or categorize a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags to add"
                            }
                        },
                        "required": ["task_id", "tags"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_tags",
                    "description": "Remove tags from a task. Use this when the user wants to remove tags from a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags to remove"
                            }
                        },
                        "required": ["task_id", "tags"]
                    }
                }
            }
        ]

    async def execute_tool(
        self,
        user_id: str,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute a tool by name with given arguments.

        Args:
            user_id: User ID for authorization
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        try:
            if tool_name == "create_task":
                return await self._create_task(user_id, arguments)
            elif tool_name == "update_task":
                return await self._update_task(user_id, arguments)
            elif tool_name == "complete_task":
                return await self._complete_task(user_id, arguments)
            elif tool_name == "delete_task":
                return await self._delete_task(user_id, arguments)
            elif tool_name == "list_tasks":
                return await self._list_tasks(user_id, arguments)
            elif tool_name == "search_tasks":
                return await self._search_tasks(user_id, arguments)
            elif tool_name == "add_tags":
                return await self._add_tags(user_id, arguments)
            elif tool_name == "remove_tags":
                return await self._remove_tags(user_id, arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _create_task(self, user_id: str, args: dict) -> dict:
        """Execute create_task tool."""
        request = TaskCreateRequest(
            title=args["title"],
            description=args.get("description"),
            priority=Priority(args["priority"]) if args.get("priority") else Priority.MEDIUM,
            tags=args.get("tags", []),
            due_at=datetime.fromisoformat(args["due_at"]) if args.get("due_at") else None,
            remind_at=datetime.fromisoformat(args["remind_at"]) if args.get("remind_at") else None,
            recurrence_pattern=RecurrencePattern(args["recurrence_pattern"]) if args.get("recurrence_pattern") else None
        )
        task = await self.task_service.create_task(user_id, request, source="chat")
        return {
            "success": True,
            "action": "create",
            "task_id": str(task.id),
            "task": task.model_dump(mode="json")
        }

    async def _update_task(self, user_id: str, args: dict) -> dict:
        """Execute update_task tool."""
        task_id = UUID(args["task_id"])
        request = TaskUpdateRequest(
            title=args.get("title"),
            description=args.get("description"),
            priority=Priority(args["priority"]) if args.get("priority") else None,
            tags=args.get("tags"),
            due_at=datetime.fromisoformat(args["due_at"]) if args.get("due_at") else None,
            remind_at=datetime.fromisoformat(args["remind_at"]) if args.get("remind_at") else None,
            recurrence_pattern=RecurrencePattern(args["recurrence_pattern"]) if args.get("recurrence_pattern") else None
        )
        task = await self.task_service.update_task(user_id, task_id, request, source="chat")
        if not task:
            return {"success": False, "error": "Task not found"}
        return {
            "success": True,
            "action": "update",
            "task_id": str(task.id),
            "task": task.model_dump(mode="json")
        }

    async def _complete_task(self, user_id: str, args: dict) -> dict:
        """Execute complete_task tool."""
        task_id = UUID(args["task_id"])
        task = await self.task_service.complete_task(user_id, task_id, source="chat")
        if not task:
            return {"success": False, "error": "Task not found"}
        return {
            "success": True,
            "action": "complete",
            "task_id": str(task.id),
            "task": task.model_dump(mode="json")
        }

    async def _delete_task(self, user_id: str, args: dict) -> dict:
        """Execute delete_task tool."""
        task_id = UUID(args["task_id"])
        success = await self.task_service.delete_task(user_id, task_id, source="chat")
        return {
            "success": success,
            "action": "delete",
            "task_id": args["task_id"]
        }

    async def _list_tasks(self, user_id: str, args: dict) -> dict:
        """Execute list_tasks tool."""
        filters = TaskFilterParams(
            status=args.get("status"),
            priority=args.get("priority"),
            tags=args.get("tags"),
            search=args.get("search"),
            sort_by=args.get("sort_by", "created_at"),
            sort_order=args.get("sort_order", "desc")
        )
        tasks, total = await self.task_service.list_tasks(user_id, filters)
        return {
            "success": True,
            "action": "list",
            "tasks": [t.model_dump(mode="json") for t in tasks],
            "total": total
        }

    async def _search_tasks(self, user_id: str, args: dict) -> dict:
        """Execute search_tasks tool."""
        tasks, total = await self.task_service.search_tasks(user_id, args["query"])
        return {
            "success": True,
            "action": "search",
            "query": args["query"],
            "tasks": [t.model_dump(mode="json") for t in tasks],
            "total": total
        }

    async def _add_tags(self, user_id: str, args: dict) -> dict:
        """Execute add_tags tool."""
        task_id = UUID(args["task_id"])
        task = await self.task_service.add_tags(user_id, task_id, args["tags"], source="chat")
        if not task:
            return {"success": False, "error": "Task not found"}
        return {
            "success": True,
            "action": "add_tags",
            "task_id": str(task.id),
            "tags": task.tags
        }

    async def _remove_tags(self, user_id: str, args: dict) -> dict:
        """Execute remove_tags tool."""
        task_id = UUID(args["task_id"])
        task = await self.task_service.remove_tags(user_id, task_id, args["tags"], source="chat")
        if not task:
            return {"success": False, "error": "Task not found"}
        return {
            "success": True,
            "action": "remove_tags",
            "task_id": str(task.id),
            "tags": task.tags
        }


# Global instance for dependency injection
_mcp_tools: Optional[MCPTools] = None


def get_mcp_tools() -> MCPTools:
    """Get or create global MCPTools instance."""
    global _mcp_tools
    if _mcp_tools is None:
        _mcp_tools = MCPTools()
    return _mcp_tools
