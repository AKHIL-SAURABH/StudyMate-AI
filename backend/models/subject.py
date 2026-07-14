"""
StudyMate AI — Subject & Topic Pydantic Models.

Defines schemas for academic subjects and their topics.
"""

from pydantic import BaseModel, Field, field_validator


class SubjectCreate(BaseModel):
    """Schema for creating a new subject."""

    name: str = Field(
        ..., min_length=1, max_length=200,
        description="Subject name (e.g., 'Mathematics', 'Physics')"
    )
    description: str = Field(
        default="",
        max_length=1000,
        description="Optional description of the subject"
    )
    difficulty_level: str = Field(
        default="medium",
        description="Difficulty level: easy, medium, hard"
    )

    @field_validator("difficulty_level")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        """Ensure difficulty level is valid."""
        allowed = {"easy", "medium", "hard"}
        if v.lower() not in allowed:
            raise ValueError(f"Difficulty must be one of: {allowed}")
        return v.lower()


class SubjectResponse(BaseModel):
    """Schema for subject data in API responses."""

    id: str
    user_id: str
    name: str
    description: str
    difficulty_level: str
    created_at: str
    topics: list["TopicResponse"] = []

    model_config = {"from_attributes": True}


class TopicCreate(BaseModel):
    """Schema for creating a new topic under a subject."""

    name: str = Field(
        ..., min_length=1, max_length=200,
        description="Topic name"
    )
    description: str = Field(
        default="",
        max_length=1000,
        description="Optional topic description"
    )
    priority: int = Field(
        default=3, ge=1, le=5,
        description="Priority level (1=lowest, 5=highest)"
    )


class TopicResponse(BaseModel):
    """Schema for topic data in API responses."""

    id: str
    subject_id: str
    name: str
    description: str
    priority: int
    status: str
    created_at: str

    model_config = {"from_attributes": True}
