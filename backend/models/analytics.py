"""
StudyMate AI — Analytics Pydantic Models.

Defines schemas for progress tracking and study analytics.
"""

from typing import Optional
from pydantic import BaseModel, Field


class TopicProgress(BaseModel):
    """Progress data for a single topic."""

    topic_id: str
    topic_name: str
    subject_name: str
    confidence_score: float
    revision_count: int
    last_reviewed: Optional[str]
    next_review: Optional[str]
    status: str


class ProgressOverview(BaseModel):
    """Overall progress summary for a user."""

    total_subjects: int
    total_topics: int
    topics_completed: int
    topics_in_progress: int
    topics_not_started: int
    average_confidence: float
    total_study_hours: float
    total_quizzes_taken: int
    average_quiz_score: float
    topic_progress: list[TopicProgress] = []


class DailyStudyData(BaseModel):
    """Study data for a single day."""

    date: str
    minutes_studied: int
    topics_covered: int
    quizzes_taken: int


class SubjectBreakdown(BaseModel):
    """Study time breakdown by subject."""

    subject_name: str
    total_minutes: int
    percentage: float
    topic_count: int


class StudyAnalytics(BaseModel):
    """Comprehensive study analytics."""

    total_study_minutes: int
    total_sessions: int
    average_session_length: float
    longest_streak_days: int
    current_streak_days: int
    daily_data: list[DailyStudyData] = []
    subject_breakdown: list[SubjectBreakdown] = []


class WeeklySummary(BaseModel):
    """Weekly study summary."""

    week_start: str
    week_end: str
    total_minutes: int
    sessions_count: int
    topics_studied: int
    quizzes_completed: int
    average_quiz_score: float
    highlights: list[str] = []
