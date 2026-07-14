"""
StudyMate AI — Chat Router.

Endpoints for AI agent chat interactions and conversation history.
"""

from fastapi import APIRouter, Depends

from backend.dependencies import get_current_user_id
from backend.models.chat import ChatRequest, ChatResponse
from agent.controller import agent_controller
from utils.logger import get_logger

logger = get_logger("chat_router")

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/message", response_model=dict)
async def send_message(
    data: ChatRequest,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """
    Send a message to the AI study mentor.

    The agent processes the message through its ReAct loop,
    potentially calling MCP tools, reflecting on results,
    and returning a comprehensive response.
    """
    logger.info("Chat message from user=%s: %s", user_id, data.message[:100])

    response: ChatResponse = await agent_controller.process_message(
        user_id=user_id,
        message=data.message,
        conversation_id=data.conversation_id,
    )

    return {"success": True, "data": response.model_dump()}


@router.get("/history/{user_id}", response_model=dict)
async def get_chat_history(
    user_id: str,
    current_user: str = Depends(get_current_user_id),
) -> dict:
    """Get conversation history for a user."""
    from backend.database import db

    rows = await db.execute(
        """SELECT conversation_id, role, content, created_at
           FROM memory
           WHERE user_id = ?
           ORDER BY created_at DESC
           LIMIT 100""",
        (user_id,),
    )

    return {"success": True, "data": rows or []}
