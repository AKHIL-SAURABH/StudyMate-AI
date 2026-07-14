"""
StudyMate AI — Quiz Pydantic Models.

Defines schemas for quiz generation, submission, and scoring.
"""

from typing import Optional
from pydantic import BaseModel, Field


class QuizGenerateRequest(BaseModel):
    """Schema for requesting quiz generation."""

    topic: str = Field(
        ..., min_length=1, max_length=200,
        description="Topic to generate quiz about"
    )
    difficulty: str = Field(
        default="medium",
        description="Quiz difficulty: easy, medium, hard"
    )
    num_questions: int = Field(
        default=5, ge=1, le=20,
        description="Number of questions (1-20)"
    )
    topic_id: Optional[str] = Field(
        default=None,
        description="Optional topic ID for tracking"
    )


class QuizQuestion(BaseModel):
    """Schema for a single quiz question."""

    question_number: int
    question: str
    options: list[str]
    correct_answer: str
    explanation: str = ""


class QuizResponse(BaseModel):
    """Schema for generated quiz data."""

    topic: str
    difficulty: str
    questions: list[QuizQuestion]
    total_questions: int


class QuizSubmitRequest(BaseModel):
    """Schema for submitting quiz answers."""

    topic_id: Optional[str] = None
    topic: str = ""
    answers: dict[str, str] = Field(
        ..., description="Map of question_number (as string) to selected answer"
    )
    quiz_data: dict = Field(
        ..., description="Original quiz data for scoring"
    )


class QuizScoreResponse(BaseModel):
    """Schema for quiz scoring results."""

    id: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    results: list[dict]
    taken_at: str
