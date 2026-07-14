"""
StudyMate AI — Study Session Service.

Handles creation and retrieval of study sessions.
"""

from typing import Optional

from backend.database import db
from backend.models.session import StudySessionCreate, StudySessionResponse
from utils.helpers import generate_id, utc_now
from utils.logger import get_logger

logger = get_logger("session_service")


class SessionService:
    """Service for study session operations."""

    async def create_session(
        self, user_id: str, data: StudySessionCreate
    ) -> StudySessionResponse:
        """
        Log a new study session.

        Args:
            user_id: User who studied.
            data: Session data.

        Returns:
            Created session response.
        """
        session_id = generate_id()
        now = utc_now()

        await db.execute(
            """INSERT INTO study_sessions
               (id, user_id, subject_id, topic_id, duration_minutes, notes, started_at, ended_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id, user_id, data.subject_id, data.topic_id,
                data.duration_minutes, data.notes, now, now,
            ),
        )

        # Update topic status to in_progress if it was not_started
        if data.topic_id:
            await db.execute(
                """UPDATE topics SET status = 'in_progress'
                   WHERE id = ? AND status = 'not_started'""",
                (data.topic_id,),
            )

        logger.info(
            "Study session logged: %d min (user=%s)", data.duration_minutes, user_id
        )

        return StudySessionResponse(
            id=session_id,
            user_id=user_id,
            subject_id=data.subject_id,
            topic_id=data.topic_id,
            duration_minutes=data.duration_minutes,
            notes=data.notes,
            started_at=now,
            ended_at=now,
        )

    async def get_sessions(
        self, user_id: str, limit: int = 50
    ) -> list[StudySessionResponse]:
        """
        Get recent study sessions for a user.

        Args:
            user_id: User identifier.
            limit: Maximum number of sessions to return.

        Returns:
            List of study sessions.
        """
        rows = await db.execute(
            """SELECT * FROM study_sessions
               WHERE user_id = ?
               ORDER BY started_at DESC
               LIMIT ?""",
            (user_id, limit),
        )
        return [StudySessionResponse(**row) for row in (rows or [])]

    async def get_total_study_minutes(self, user_id: str) -> int:
        """Get total study minutes for a user."""
        result = await db.execute_scalar(
            "SELECT COALESCE(SUM(duration_minutes), 0) FROM study_sessions WHERE user_id = ?",
            (user_id,),
        )
        return int(result or 0)

    async def get_session_count(self, user_id: str) -> int:
        """Get total number of study sessions."""
        result = await db.execute_scalar(
            "SELECT COUNT(*) FROM study_sessions WHERE user_id = ?",
            (user_id,),
        )
        return int(result or 0)


# Singleton instance
session_service = SessionService()
