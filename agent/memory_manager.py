"""
StudyMate AI — Memory Manager.

Handles conversation memory persistence and retrieval.
Supports short-term (in-conversation) and long-term (across sessions) memory.
"""

import json
from typing import Optional

from backend.config import get_settings
from backend.database import db
from utils.helpers import generate_id, utc_now
from utils.logger import get_logger

logger = get_logger("memory")


class MemoryManager:
    """
    Manages conversation memory for the AI agent.

    - Short-term: Current conversation messages (in-memory)
    - Long-term: Persisted conversation history (SQLite)
    """

    def __init__(self) -> None:
        self._settings = get_settings()

    async def load_context(
        self, user_id: str, conversation_id: Optional[str] = None
    ) -> list[dict[str, str]]:
        """
        Load conversation context for the agent.

        Retrieves recent messages from the current conversation
        and summarized context from previous conversations.

        Args:
            user_id: User identifier.
            conversation_id: Current conversation ID.

        Returns:
            List of message dicts with 'role' and 'content' keys.
        """
        window = self._settings.agent_memory_window
        messages = []

        if conversation_id:
            # Load messages from the current conversation
            rows = await db.execute(
                """SELECT role, content FROM memory
                   WHERE user_id = ? AND conversation_id = ?
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (user_id, conversation_id, window),
            )
            if rows:
                # Reverse to chronological order
                messages = [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

        # If no current conversation messages, load recent from any conversation
        if not messages:
            rows = await db.execute(
                """SELECT role, content FROM memory
                   WHERE user_id = ?
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (user_id, min(window, 10)),
            )
            if rows:
                messages = [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

        logger.info("Loaded %d context messages for user=%s", len(messages), user_id)
        return messages

    async def save_message(
        self,
        user_id: str,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Save a message to conversation memory.

        Args:
            user_id: User identifier.
            conversation_id: Conversation identifier.
            role: Message role ('user' or 'assistant').
            content: Message content.
            metadata: Optional metadata dict.
        """
        await db.execute(
            """INSERT INTO memory (id, user_id, conversation_id, role, content, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                generate_id(),
                user_id,
                conversation_id,
                role,
                content,
                json.dumps(metadata or {}),
                utc_now(),
            ),
        )

    async def save_agent_log(
        self,
        user_id: str,
        conversation_id: str,
        step_type: str,
        content: str,
        step_number: int,
        tool_name: Optional[str] = None,
        tool_input: Optional[dict] = None,
        tool_output: Optional[str] = None,
    ) -> None:
        """
        Save an agent reasoning step to the audit log.

        Args:
            user_id: User identifier.
            conversation_id: Conversation identifier.
            step_type: Step type (thought/action/observation/reflection/final).
            content: Step content.
            step_number: Sequential step number.
            tool_name: Name of tool used (if any).
            tool_input: Tool input arguments (if any).
            tool_output: Tool output (if any).
        """
        await db.execute(
            """INSERT INTO agent_logs
               (id, user_id, conversation_id, step_type, content,
                tool_name, tool_input, tool_output, step_number, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                generate_id(),
                user_id,
                conversation_id,
                step_type,
                content,
                tool_name,
                json.dumps(tool_input) if tool_input else None,
                tool_output,
                step_number,
                utc_now(),
            ),
        )

    async def get_agent_logs(
        self, user_id: str, conversation_id: str
    ) -> list[dict]:
        """Get agent reasoning logs for a conversation."""
        rows = await db.execute(
            """SELECT * FROM agent_logs
               WHERE user_id = ? AND conversation_id = ?
               ORDER BY step_number ASC""",
            (user_id, conversation_id),
        )
        return rows or []


# Singleton instance
memory_manager = MemoryManager()
