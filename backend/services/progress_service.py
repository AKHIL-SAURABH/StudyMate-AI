"""
StudyMate AI — Progress Service.

Handles topic-level progress tracking with confidence scores and revision scheduling.
"""

from typing import Optional
from datetime import datetime, timedelta, timezone

from backend.database import db
from backend.models.analytics import ProgressOverview, TopicProgress
from utils.helpers import generate_id, utc_now, calculate_percentage
from utils.logger import get_logger

logger = get_logger("progress_service")


class ProgressService:
    """Service for progress tracking operations."""

    async def update_progress(
        self,
        user_id: str,
        topic_id: str,
        confidence_score: float,
    ) -> None:
        """
        Update or create progress entry for a topic.

        Uses spaced repetition logic to calculate the next review date
        based on current confidence and revision count.

        Args:
            user_id: User identifier.
            topic_id: Topic identifier.
            confidence_score: Confidence level (0.0 to 1.0).
        """
        now = utc_now()

        existing = await db.execute_one(
            "SELECT * FROM progress WHERE user_id = ? AND topic_id = ?",
            (user_id, topic_id),
        )

        if existing:
            revision_count = existing["revision_count"] + 1
            next_review = self._calculate_next_review(confidence_score, revision_count)

            await db.execute(
                """UPDATE progress
                   SET confidence_score = ?, revision_count = ?,
                       last_reviewed = ?, next_review = ?
                   WHERE user_id = ? AND topic_id = ?""",
                (confidence_score, revision_count, now, next_review, user_id, topic_id),
            )
        else:
            next_review = self._calculate_next_review(confidence_score, 1)
            await db.execute(
                """INSERT INTO progress
                   (id, user_id, topic_id, confidence_score, revision_count,
                    last_reviewed, next_review)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (generate_id(), user_id, topic_id, confidence_score, 1, now, next_review),
            )

        # Update topic status based on confidence
        if confidence_score >= 0.8:
            await db.execute(
                "UPDATE topics SET status = 'completed' WHERE id = ?",
                (topic_id,),
            )
        elif confidence_score > 0:
            await db.execute(
                "UPDATE topics SET status = 'in_progress' WHERE id = ?",
                (topic_id,),
            )

        logger.info(
            "Progress updated: topic=%s confidence=%.2f", topic_id, confidence_score
        )

    async def get_overview(self, user_id: str) -> ProgressOverview:
        """
        Get a comprehensive progress overview for a user.

        Args:
            user_id: User identifier.

        Returns:
            ProgressOverview with all metrics.
        """
        # Count subjects
        total_subjects = await db.execute_scalar(
            "SELECT COUNT(*) FROM subjects WHERE user_id = ?", (user_id,)
        ) or 0

        # Count topics by status
        topic_stats = await db.execute(
            """SELECT t.status, COUNT(*) as count
               FROM topics t
               JOIN subjects s ON t.subject_id = s.id
               WHERE s.user_id = ?
               GROUP BY t.status""",
            (user_id,),
        )

        status_counts = {row["status"]: row["count"] for row in (topic_stats or [])}
        total_topics = sum(status_counts.values())
        completed = status_counts.get("completed", 0)
        in_progress = status_counts.get("in_progress", 0)
        not_started = status_counts.get("not_started", 0)

        # Average confidence
        avg_confidence = await db.execute_scalar(
            "SELECT COALESCE(AVG(confidence_score), 0) FROM progress WHERE user_id = ?",
            (user_id,),
        ) or 0

        # Total study hours
        total_minutes = await db.execute_scalar(
            "SELECT COALESCE(SUM(duration_minutes), 0) FROM study_sessions WHERE user_id = ?",
            (user_id,),
        ) or 0

        # Quiz stats
        total_quizzes = await db.execute_scalar(
            "SELECT COUNT(*) FROM quiz_scores WHERE user_id = ?", (user_id,)
        ) or 0

        avg_quiz = await db.execute_scalar(
            "SELECT COALESCE(AVG(score_percentage), 0) FROM quiz_scores WHERE user_id = ?",
            (user_id,),
        ) or 0

        # Topic-level progress
        topic_progress = await self._get_topic_progress(user_id)

        return ProgressOverview(
            total_subjects=int(total_subjects),
            total_topics=int(total_topics),
            topics_completed=int(completed),
            topics_in_progress=int(in_progress),
            topics_not_started=int(not_started),
            average_confidence=round(float(avg_confidence), 2),
            total_study_hours=round(int(total_minutes) / 60, 1),
            total_quizzes_taken=int(total_quizzes),
            average_quiz_score=round(float(avg_quiz), 1),
            topic_progress=topic_progress,
        )

    async def _get_topic_progress(self, user_id: str) -> list[TopicProgress]:
        """Get detailed progress for each topic."""
        rows = await db.execute(
            """SELECT t.id as topic_id, t.name as topic_name, t.status,
                      s.name as subject_name,
                      COALESCE(p.confidence_score, 0) as confidence_score,
                      COALESCE(p.revision_count, 0) as revision_count,
                      p.last_reviewed, p.next_review
               FROM topics t
               JOIN subjects s ON t.subject_id = s.id
               LEFT JOIN progress p ON t.id = p.topic_id AND p.user_id = ?
               WHERE s.user_id = ?
               ORDER BY t.priority DESC""",
            (user_id, user_id),
        )

        return [
            TopicProgress(
                topic_id=row["topic_id"],
                topic_name=row["topic_name"],
                subject_name=row["subject_name"],
                confidence_score=row["confidence_score"],
                revision_count=row["revision_count"],
                last_reviewed=row["last_reviewed"],
                next_review=row["next_review"],
                status=row["status"],
            )
            for row in (rows or [])
        ]

    def _calculate_next_review(self, confidence: float, revision_count: int) -> str:
        """
        Calculate next review date using simplified spaced repetition.

        Higher confidence and more revisions push the next review further out.

        Args:
            confidence: Current confidence score (0.0 to 1.0).
            revision_count: Number of times revised.

        Returns:
            ISO 8601 datetime string for the next review.
        """
        # Base interval grows with revision count, scaled by confidence
        base_days = min(revision_count * 2, 30)
        confidence_multiplier = max(confidence, 0.1)
        days_until_review = max(1, int(base_days * confidence_multiplier))

        next_review = datetime.now(timezone.utc) + timedelta(days=days_until_review)
        return next_review.isoformat()


# Singleton instance
progress_service = ProgressService()
