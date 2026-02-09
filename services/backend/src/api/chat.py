# T038 - Chat API Endpoint
# Phase V Todo Chatbot - Natural Language Chat API
"""
POST /api/chat endpoint for processing natural language task commands.
"""

from fastapi import APIRouter, Depends, Header, HTTPException

from ..models.schemas import ChatRequest, ChatResponse
from ..services.chat_handler import ChatHandler, get_chat_handler

router = APIRouter()


def get_user_id(authorization: str = Header(default="Bearer default-user", description="Bearer token")) -> str:
    """Extract user ID from authorization header."""
    if not authorization.startswith("Bearer "):
        return "default-user"
    token = authorization[7:]
    return token if token else "default-user"


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Process chat message",
    description="Process a natural language message and execute task operations"
)
async def process_chat(
    request: ChatRequest,
    user_id: str = Depends(get_user_id),
    chat_handler: ChatHandler = Depends(get_chat_handler)
) -> ChatResponse:
    """
    Process a natural language chat message.

    The message is parsed using LLM function calling to determine the intent
    and execute the appropriate task operation (create, update, complete, delete, list, etc.).

    Example messages:
    - "Add task: Buy groceries with high priority"
    - "Show my tasks"
    - "Mark Buy groceries as complete"
    - "Delete the groceries task"
    - "Find tasks about shopping"
    """
    return await chat_handler.process_message(user_id, request)
