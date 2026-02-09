# T037, T054, T062, T071, T079, T093 - Chat Handler
# Phase V Todo Chatbot - Natural Language Chat Processing
"""
ChatHandler processes natural language messages and executes task operations.
Uses OpenAI API for NL understanding with function calling.
"""

import json
import os
from typing import Any, Optional

import httpx
import structlog

from ..mcp.tools import MCPTools, get_mcp_tools
from ..models.schemas import ChatRequest, ChatResponse

logger = structlog.get_logger()

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


SYSTEM_PROMPT = """You are a helpful task management assistant. You help users manage their todo tasks through natural language.

Available actions:
- Create tasks with title, description, priority (High/Medium/Low), tags, due dates, reminders, and recurrence patterns
- Update existing tasks
- Mark tasks as completed
- Delete tasks
- List and filter tasks by status, priority, tags
- Search tasks by text
- Add or remove tags from tasks

When the user wants to:
- Add/create/make a task → use create_task
- Change/update/modify a task → use update_task
- Complete/finish/done with a task → use complete_task
- Remove/delete a task → use delete_task
- See/show/list tasks → use list_tasks
- Find/search for tasks → use search_tasks
- Tag/categorize a task → use add_tags
- Remove tags → use remove_tags

For dates, convert natural language like "tomorrow", "next week", "in 2 hours" to ISO 8601 format.
For priorities, map words like "urgent", "important", "asap" to "High", normal to "Medium", and "low priority", "whenever" to "Low".

Always be helpful and confirm what action you're taking."""


class ChatHandler:
    """
    Handles natural language chat messages.
    Uses OpenAI function calling to map user intent to task operations.
    """

    def __init__(self, mcp_tools: Optional[MCPTools] = None):
        """Initialize with optional MCP tools for testing."""
        self.mcp_tools = mcp_tools or get_mcp_tools()
        self.api_key = OPENAI_API_KEY

    async def process_message(
        self,
        user_id: str,
        request: ChatRequest
    ) -> ChatResponse:
        """
        Process a natural language chat message.

        Args:
            user_id: User ID for authorization
            request: Chat request with message

        Returns:
            ChatResponse with assistant response and action result
        """
        if not self.api_key:
            # Fallback to simple pattern matching if no API key
            return await self._process_without_llm(user_id, request)

        try:
            # Call OpenAI with function definitions
            response = await self._call_openai(request.message)

            # Check if function call is needed
            if response.get("function_call"):
                return await self._execute_function(user_id, response)

            # No function call - just return the response
            return ChatResponse(
                response=response.get("content", "I'm not sure how to help with that. Try asking me to create, update, complete, delete, or list tasks.")
            )

        except Exception as e:
            logger.error("chat_processing_error", error=str(e))
            return ChatResponse(
                response=f"Sorry, I encountered an error processing your request. Please try again."
            )

    async def _call_openai(self, message: str) -> dict[str, Any]:
        """Call OpenAI API with function definitions."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OPENAI_API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": message}
                    ],
                    "tools": self.mcp_tools.get_tool_definitions(),
                    "tool_choice": "auto"
                }
            )
            response.raise_for_status()
            data = response.json()

            choice = data["choices"][0]["message"]

            # Check for tool calls
            if choice.get("tool_calls"):
                tool_call = choice["tool_calls"][0]
                return {
                    "function_call": {
                        "name": tool_call["function"]["name"],
                        "arguments": json.loads(tool_call["function"]["arguments"])
                    },
                    "content": choice.get("content")
                }

            return {"content": choice.get("content", "")}

    async def _execute_function(
        self,
        user_id: str,
        response: dict[str, Any]
    ) -> ChatResponse:
        """Execute the function call and generate response."""
        func_call = response["function_call"]
        tool_name = func_call["name"]
        arguments = func_call["arguments"]

        logger.info("executing_tool", tool=tool_name, args=arguments)

        # Execute the tool
        result = await self.mcp_tools.execute_tool(user_id, tool_name, arguments)

        # Generate response based on result
        if result.get("error"):
            return ChatResponse(
                response=f"Sorry, I couldn't complete that action: {result['error']}"
            )

        action = result.get("action", tool_name)
        task_id = result.get("task_id")

        # Build response message based on action
        if action == "create":
            task = result.get("task", {})
            msg = f"✅ Created task: **{task.get('title')}**"
            if task.get("priority") != "Medium":
                msg += f" ({task.get('priority')} priority)"
            if task.get("due_at"):
                msg += f"\n📅 Due: {task.get('due_at')}"
            if task.get("remind_at"):
                msg += f"\n🔔 Reminder set"
            if task.get("recurrence_pattern"):
                msg += f"\n🔄 Repeats: {task.get('recurrence_pattern')}"

        elif action == "update":
            msg = "✅ Task updated successfully"

        elif action == "complete":
            task = result.get("task", {})
            msg = f"✅ Marked **{task.get('title')}** as complete"

        elif action == "delete":
            msg = "✅ Task deleted"

        elif action == "list":
            tasks = result.get("tasks", [])
            total = result.get("total", 0)
            if not tasks:
                msg = "📋 No tasks found"
            else:
                msg = f"📋 Found {total} task(s):\n"
                for i, task in enumerate(tasks[:10], 1):
                    status = "✅" if task.get("status") == "completed" else "⬜"
                    msg += f"\n{i}. {status} **{task.get('title')}**"
                    if task.get("priority") == "High":
                        msg += " 🔴"
                    if task.get("due_at"):
                        msg += f" (due: {task.get('due_at')[:10]})"
                if total > 10:
                    msg += f"\n... and {total - 10} more"

        elif action == "search":
            tasks = result.get("tasks", [])
            query = result.get("query", "")
            if not tasks:
                msg = f"🔍 No tasks found matching '{query}'"
            else:
                msg = f"🔍 Found {len(tasks)} task(s) matching '{query}':\n"
                for task in tasks[:5]:
                    msg += f"\n• **{task.get('title')}**"

        elif action in ("add_tags", "remove_tags"):
            tags = result.get("tags", [])
            msg = f"🏷️ Tags updated: {', '.join(tags) if tags else 'none'}"

        else:
            msg = "✅ Done"

        return ChatResponse(
            response=msg,
            task_id=task_id,
            action=action
        )

    async def _process_without_llm(
        self,
        user_id: str,
        request: ChatRequest
    ) -> ChatResponse:
        """
        Simple pattern matching fallback when no LLM API key is available.
        """
        message = request.message.lower()

        # Simple command parsing
        if any(word in message for word in ["add", "create", "new"]):
            # Extract title after command words
            title = request.message
            for word in ["add task:", "create task:", "add:", "create:", "new task:", "add task", "create task"]:
                title = title.replace(word, "").replace(word.lower(), "")
            title = title.strip()

            if title:
                from ..models.schemas import TaskCreateRequest
                from ..services.task_service import get_task_service

                task_service = get_task_service()
                task_request = TaskCreateRequest(title=title)
                task = await task_service.create_task(user_id, task_request, source="chat")

                return ChatResponse(
                    response=f"✅ Created task: **{task.title}**",
                    task_id=task.id,
                    action="create"
                )

        elif any(word in message for word in ["list", "show", "see", "view"]):
            from ..services.task_service import get_task_service

            task_service = get_task_service()
            tasks, total = await task_service.list_tasks(user_id)

            if not tasks:
                return ChatResponse(response="📋 No tasks found", action="list")

            msg = f"📋 You have {total} task(s):\n"
            for i, task in enumerate(tasks[:10], 1):
                status = "✅" if task.status == "completed" else "⬜"
                msg += f"\n{i}. {status} **{task.title}**"

            return ChatResponse(response=msg, action="list")

        return ChatResponse(
            response="I can help you manage tasks! Try:\n• 'Add task: <title>'\n• 'Show my tasks'\n• 'Complete <task>'\n• 'Delete <task>'"
        )


# Global instance for dependency injection
_chat_handler: Optional[ChatHandler] = None


def get_chat_handler() -> ChatHandler:
    """Get or create global ChatHandler instance."""
    global _chat_handler
    if _chat_handler is None:
        _chat_handler = ChatHandler()
    return _chat_handler
