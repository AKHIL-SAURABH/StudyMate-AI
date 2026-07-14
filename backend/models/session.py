"""
StudyMate AI — Study Session Pydantic Models.

Defines schemas for study session tracking and logging.
"""

from typing import Optional
from pydantic import BaseModel, Field


class StudySessionCreate(BaseModel):
    """Schema for logging a study session."""

    subject_id: Optional[str] = Field(
        default=None, description="Subject ID for this session"
    )
    topic_id: Optional[str] = Field(
        default=None, description="Topic ID for this session"
    )
    duration_minutes: int = Field(
        ..., ge=1, le=720,
        description="Session duration in minutes (1-720)"
    )
    notes: str = Field(
        default="",
        max_length=2000,
        description="Optional session notes"
    )


class StudySessionResponse(BaseModel):
    """Schema for study session data in API responses."""

    id: str
    user_id: str
    subject_id: Optional[str]
    topic_id: Optional[str]
    duration_minutes: int
    notes: str
    started_at: str
    ended_at: Optional[str]

    model_config = {"from_attributes": True}
