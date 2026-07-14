"""
StudyMate AI — Chat Pydantic Models.

Defines schemas for AI agent chat interactions and response structures.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Schema for sending a message to the AI agent."""

    message: str = Field(
        ..., min_length=1, max_length=5000,
        description="User message to the AI study mentor"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Conversation ID for context continuity"
    )


class AgentStep(BaseModel):
    """Schema representing a single step in the agent's reasoning."""

    step_number: int
    step_type: str = Field(
        ..., description="Type: thought, action, observation, reflection, final"
    )
    content: str = ""
    tool_name: Optional[str] = None
    tool_input: Optional[dict] = None
    tool_output: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for the AI agent's response."""

    conversation_id: str
    response: str = Field(..., description="Final agent response text")
    agent_steps: list[AgentStep] = Field(
        default_factory=list,
        description="Agent's reasoning steps (visible in debug mode)"
    )
    tools_used: list[str] = Field(
        default_factory=list,
        description="Names of MCP tools invoked during reasoning"
    )
