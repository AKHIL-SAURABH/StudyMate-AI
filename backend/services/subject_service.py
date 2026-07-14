"""
StudyMate AI — Subject & Topic Service.

Handles CRUD operations for academic subjects and their topics.
"""


from backend.database import db
from backend.exceptions import ResourceNotFoundError
from backend.models.subject import (
    SubjectCreate,
    SubjectResponse,
    TopicCreate,
    TopicResponse,
)
from utils.helpers import generate_id, utc_now
from utils.logger import get_logger

logger = get_logger("subject_service")


class SubjectService:
    """Service for subject and topic management."""

    async def create_subject(self, user_id: str, data: SubjectCreate) -> SubjectResponse:
        """
        Create a new subject for a user.

        Args:
            user_id: Owner user ID.
            data: Subject creation data.

        Returns:
            Created subject response.
        """
        subject_id = generate_id()
        now = utc_now()

        await db.execute(
            """INSERT INTO subjects (id, user_id, name, description, difficulty_level, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (subject_id, user_id, data.name, data.description, data.difficulty_level, now),
        )

        logger.info("Subject created: %s (user=%s)", data.name, user_id)

        return SubjectResponse(
            id=subject_id,
            user_id=user_id,
            name=data.name,
            description=data.description,
            difficulty_level=data.difficulty_level,
            created_at=now,
            topics=[],
        )

    async def get_subjects(self, user_id: str) -> list[SubjectResponse]:
        """
        Get all subjects for a user, including their topics.

        Args:
            user_id: User identifier.

        Returns:
            List of subjects with nested topics.
        """
        subjects = await db.execute(
            "SELECT * FROM subjects WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )

        result = []
        for subj in subjects or []:
            topics = await db.execute(
                "SELECT * FROM topics WHERE subject_id = ? ORDER BY priority DESC",
                (subj["id"],),
            )
            topic_list = [TopicResponse(**t) for t in (topics or [])]
            result.append(SubjectResponse(**subj, topics=topic_list))

        return result

    async def get_subject(self, subject_id: str) -> SubjectResponse:
        """
        Get a single subject by ID.

        Args:
            subject_id: Subject identifier.

        Returns:
            Subject with topics.

        Raises:
            ResourceNotFoundError: If subject doesn't exist.
        """
        subj = await db.execute_one(
            "SELECT * FROM subjects WHERE id = ?", (subject_id,)
        )
        if not subj:
            raise ResourceNotFoundError("Subject", subject_id)

        topics = await db.execute(
            "SELECT * FROM topics WHERE subject_id = ? ORDER BY priority DESC",
            (subject_id,),
        )
        topic_list = [TopicResponse(**t) for t in (topics or [])]

        return SubjectResponse(**subj, topics=topic_list)

    async def create_topic(self, subject_id: str, data: TopicCreate) -> TopicResponse:
        """
        Create a new topic under a subject.

        Args:
            subject_id: Parent subject ID.
            data: Topic creation data.

        Returns:
            Created topic response.

        Raises:
            ResourceNotFoundError: If subject doesn't exist.
        """
        # Verify subject exists
        subj = await db.execute_one(
            "SELECT id FROM subjects WHERE id = ?", (subject_id,)
        )
        if not subj:
            raise ResourceNotFoundError("Subject", subject_id)

        topic_id = generate_id()
        now = utc_now()

        await db.execute(
            """INSERT INTO topics (id, subject_id, name, description, priority, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (topic_id, subject_id, data.name, data.description, data.priority, "not_started", now),
        )

        logger.info("Topic created: %s (subject=%s)", data.name, subject_id)

        return TopicResponse(
            id=topic_id,
            subject_id=subject_id,
            name=data.name,
            description=data.description,
            priority=data.priority,
            status="not_started",
            created_at=now,
        )

    async def get_topics(self, subject_id: str) -> list[TopicResponse]:
        """
        Get all topics for a subject.

        Args:
            subject_id: Subject identifier.

        Returns:
            List of topics.
        """
        topics = await db.execute(
            "SELECT * FROM topics WHERE subject_id = ? ORDER BY priority DESC",
            (subject_id,),
        )
        return [TopicResponse(**t) for t in (topics or [])]

    async def update_topic_status(self, topic_id: str, status: str) -> None:
        """
        Update a topic's study status.

        Args:
            topic_id: Topic identifier.
            status: New status (not_started, in_progress, completed).
        """
        valid_statuses = {"not_started", "in_progress", "completed"}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        await db.execute(
            "UPDATE topics SET status = ? WHERE id = ?",
            (status, topic_id),
        )

    async def delete_topic(self, topic_id: str) -> None:
        """Delete a topic by ID."""
        await db.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
        logger.info("Topic deleted: %s", topic_id)

    async def delete_subject(self, subject_id: str) -> None:
        """Delete a subject and its topics (cascade)."""
        await db.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        logger.info("Subject deleted: %s", subject_id)

    async def get_all_user_topics(self, user_id: str) -> list[dict]:
        """
        Get all topics across all subjects for a user.

        Args:
            user_id: User identifier.

        Returns:
            List of topic dicts with subject names.
        """
        rows = await db.execute(
            """SELECT t.*, s.name as subject_name
               FROM topics t
               JOIN subjects s ON t.subject_id = s.id
               WHERE s.user_id = ?
               ORDER BY t.priority DESC""",
            (user_id,),
        )
        return rows or []


# Singleton instance
subject_service = SubjectService()
