"""
StudyMate AI — Analytics Service.

Computes study analytics, weekly summaries, and subject breakdowns.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from backend.database import db
from backend.models.analytics import (
    StudyAnalytics,
    WeeklySummary,
    DailyStudyData,
    SubjectBreakdown,
)
from utils.helpers import calculate_percentage
from utils.logger import get_logger

logger = get_logger("analytics_service")


class AnalyticsService:
    """Service for computing study analytics."""

    async def get_analytics(self, user_id: str) -> StudyAnalytics:
        """
        Get comprehensive study analytics for a user.

        Args:
            user_id: User identifier.

        Returns:
            StudyAnalytics with all computed metrics.
        """
        # Total study minutes and sessions
        totals = await db.execute_one(
            """SELECT COALESCE(SUM(duration_minutes), 0) as total_minutes,
                      COUNT(*) as total_sessions
               FROM study_sessions WHERE user_id = ?""",
            (user_id,),
        )

        total_minutes = totals["total_minutes"] if totals else 0
        total_sessions = totals["total_sessions"] if totals else 0
        avg_session = round(total_minutes / max(total_sessions, 1), 1)

        # Daily study data (last 30 days)
        daily_data = await self._get_daily_data(user_id, days=30)

        # Subject breakdown
        subject_breakdown = await self._get_subject_breakdown(user_id, total_minutes)

        # Streak calculation
        current_streak, longest_streak = self._calculate_streaks(daily_data)

        return StudyAnalytics(
            total_study_minutes=int(total_minutes),
            total_sessions=int(total_sessions),
            average_session_length=avg_session,
            longest_streak_days=longest_streak,
            current_streak_days=current_streak,
            daily_data=daily_data,
            subject_breakdown=subject_breakdown,
        )

    async def get_weekly_summary(self, user_id: str) -> WeeklySummary:
        """
        Get the current week's study summary.

        Args:
            user_id: User identifier.

        Returns:
            WeeklySummary with this week's metrics.
        """
        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)

        # Study stats for the week
        stats = await db.execute_one(
            """SELECT COALESCE(SUM(duration_minutes), 0) as total_minutes,
                      COUNT(*) as sessions_count,
                      COUNT(DISTINCT topic_id) as topics_studied
               FROM study_sessions
               WHERE user_id = ? AND started_at >= ? AND started_at < ?""",
            (user_id, week_start.isoformat(), week_end.isoformat()),
        )

        # Quiz stats for the week
        quiz_stats = await db.execute_one(
            """SELECT COUNT(*) as quizzes,
                      COALESCE(AVG(score_percentage), 0) as avg_score
               FROM quiz_scores
               WHERE user_id = ? AND taken_at >= ? AND taken_at < ?""",
            (user_id, week_start.isoformat(), week_end.isoformat()),
        )

        highlights = await self._generate_highlights(user_id, stats, quiz_stats)

        return WeeklySummary(
            week_start=week_start.strftime("%Y-%m-%d"),
            week_end=week_end.strftime("%Y-%m-%d"),
            total_minutes=stats["total_minutes"] if stats else 0,
            sessions_count=stats["sessions_count"] if stats else 0,
            topics_studied=stats["topics_studied"] if stats else 0,
            quizzes_completed=quiz_stats["quizzes"] if quiz_stats else 0,
            average_quiz_score=round(quiz_stats["avg_score"], 1) if quiz_stats else 0,
            highlights=highlights,
        )

    async def _get_daily_data(self, user_id: str, days: int = 30) -> list[DailyStudyData]:
        """Get daily study data for the last N days."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        rows = await db.execute(
            """SELECT DATE(started_at) as date,
                      SUM(duration_minutes) as minutes_studied,
                      COUNT(DISTINCT topic_id) as topics_covered
               FROM study_sessions
               WHERE user_id = ? AND started_at >= ?
               GROUP BY DATE(started_at)
               ORDER BY date""",
            (user_id, cutoff),
        )

        # Also get quiz counts per day
        quiz_rows = await db.execute(
            """SELECT DATE(taken_at) as date, COUNT(*) as quizzes
               FROM quiz_scores
               WHERE user_id = ? AND taken_at >= ?
               GROUP BY DATE(taken_at)""",
            (user_id, cutoff),
        )

        quiz_map = {r["date"]: r["quizzes"] for r in (quiz_rows or [])}

        return [
            DailyStudyData(
                date=row["date"],
                minutes_studied=int(row["minutes_studied"]),
                topics_covered=int(row["topics_covered"]),
                quizzes_taken=quiz_map.get(row["date"], 0),
            )
            for row in (rows or [])
        ]

    async def _get_subject_breakdown(
        self, user_id: str, total_minutes: int
    ) -> list[SubjectBreakdown]:
        """Get study time breakdown by subject."""
        rows = await db.execute(
            """SELECT s.name as subject_name,
                      COALESCE(SUM(ss.duration_minutes), 0) as total_minutes,
                      COUNT(DISTINCT t.id) as topic_count
               FROM subjects s
               LEFT JOIN study_sessions ss ON s.id = ss.subject_id
               LEFT JOIN topics t ON s.id = t.subject_id
               WHERE s.user_id = ?
               GROUP BY s.id, s.name
               ORDER BY total_minutes DESC""",
            (user_id,),
        )

        return [
            SubjectBreakdown(
                subject_name=row["subject_name"],
                total_minutes=int(row["total_minutes"]),
                percentage=calculate_percentage(row["total_minutes"], total_minutes),
                topic_count=int(row["topic_count"]),
            )
            for row in (rows or [])
        ]

    def _calculate_streaks(self, daily_data: list[DailyStudyData]) -> tuple[int, int]:
        """
        Calculate current and longest study streaks.

        Returns:
            Tuple of (current_streak, longest_streak) in days.
        """
        if not daily_data:
            return 0, 0

        dates_studied = set()
        for d in daily_data:
            if d.minutes_studied > 0:
                dates_studied.add(d.date)

        if not dates_studied:
            return 0, 0

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Current streak
        current_streak = 0
        check_date = datetime.now(timezone.utc)
        while True:
            date_str = check_date.strftime("%Y-%m-%d")
            if date_str in dates_studied:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        # Longest streak
        sorted_dates = sorted(dates_studied)
        longest = 1
        current = 1
        for i in range(1, len(sorted_dates)):
            prev = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d")
            curr = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
            if (curr - prev).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1

        return current_streak, longest

    async def _generate_highlights(
        self, user_id: str, stats: dict, quiz_stats: dict
    ) -> list[str]:
        """Generate weekly highlight messages."""
        highlights = []

        minutes = stats["total_minutes"] if stats else 0
        if minutes > 0:
            hours = round(minutes / 60, 1)
            highlights.append(f"📚 You studied for {hours} hours this week")

        sessions = stats["sessions_count"] if stats else 0
        if sessions > 0:
            highlights.append(f"🎯 Completed {sessions} study sessions")

        quizzes = quiz_stats["quizzes"] if quiz_stats else 0
        if quizzes > 0:
            avg = round(quiz_stats["avg_score"], 1) if quiz_stats else 0
            highlights.append(f"✅ Took {quizzes} quizzes with {avg}% average score")

        if not highlights:
            highlights.append("🌟 Start studying to see your weekly highlights!")

        return highlights


# Singleton instance
analytics_service = AnalyticsService()
