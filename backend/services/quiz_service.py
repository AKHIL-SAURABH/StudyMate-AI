"""
StudyMate AI — Quiz Service.

Handles quiz score persistence and retrieval.
"""

import json
from typing import Optional

from backend.database import db
from backend.models.quiz import QuizScoreResponse
from utils.helpers import generate_id, utc_now, calculate_percentage
from utils.logger import get_logger

logger = get_logger("quiz_service")


class QuizService:
    """Service for quiz score operations."""

    async def save_score(
        self,
        user_id: str,
        topic_id: Optional[str],
        total_questions: int,
        correct_answers: int,
        quiz_data: dict,
    ) -> QuizScoreResponse:
        """
        Save a quiz score.

        Args:
            user_id: User who took the quiz.
            topic_id: Optional topic ID.
            total_questions: Number of questions.
            correct_answers: Number of correct answers.
            quiz_data: Full quiz data for reference.

        Returns:
            Saved quiz score response.
        """
        score_id = generate_id()
        now = utc_now()
        score_pct = calculate_percentage(correct_answers, total_questions)

        await db.execute(
            """INSERT INTO quiz_scores
               (id, user_id, topic_id, total_questions, correct_answers,
                score_percentage, quiz_data, taken_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                score_id, user_id, topic_id, total_questions,
                correct_answers, score_pct, json.dumps(quiz_data), now,
            ),
        )

        logger.info(
            "Quiz score saved: %d/%d (%.1f%%) for user=%s",
            correct_answers, total_questions, score_pct, user_id,
        )

        return QuizScoreResponse(
            id=score_id,
            total_questions=total_questions,
            correct_answers=correct_answers,
            score_percentage=score_pct,
            results=quiz_data.get("results", []),
            taken_at=now,
        )

    async def get_history(
        self, user_id: str, limit: int = 20
    ) -> list[QuizScoreResponse]:
        """
        Get quiz score history for a user.

        Args:
            user_id: User identifier.
            limit: Maximum results.

        Returns:
            List of quiz scores.
        """
        rows = await db.execute(
            """SELECT * FROM quiz_scores
               WHERE user_id = ?
               ORDER BY taken_at DESC
               LIMIT ?""",
            (user_id, limit),
        )

        results = []
        for row in rows or []:
            quiz_data = json.loads(row.get("quiz_data", "{}"))
            results.append(
                QuizScoreResponse(
                    id=row["id"],
                    total_questions=row["total_questions"],
                    correct_answers=row["correct_answers"],
                    score_percentage=row["score_percentage"],
                    results=quiz_data.get("results", []),
                    taken_at=row["taken_at"],
                )
            )

        return results

    async def get_average_score(self, user_id: str) -> float:
        """Get average quiz score for a user."""
        result = await db.execute_scalar(
            "SELECT COALESCE(AVG(score_percentage), 0) FROM quiz_scores WHERE user_id = ?",
            (user_id,),
        )
        return round(float(result or 0), 1)

    async def get_quiz_count(self, user_id: str) -> int:
        """Get total number of quizzes taken."""
        result = await db.execute_scalar(
            "SELECT COUNT(*) FROM quiz_scores WHERE user_id = ?",
            (user_id,),
        )
        return int(result or 0)

    async def get_topic_scores(self, user_id: str, topic_id: str) -> list[dict]:
        """Get all quiz scores for a specific topic."""
        rows = await db.execute(
            """SELECT score_percentage, taken_at FROM quiz_scores
               WHERE user_id = ? AND topic_id = ?
               ORDER BY taken_at DESC""",
            (user_id, topic_id),
        )
        return rows or []


# Singleton instance
quiz_service = QuizService()
