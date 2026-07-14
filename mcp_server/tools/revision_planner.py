"""
StudyMate AI — Revision Planner Tool.

Creates spaced-repetition revision schedules based on quiz scores and confidence.
"""

import json
from datetime import datetime, timedelta


def register_tools(mcp) -> None:
    """Register revision planner tools with the MCP server."""

    @mcp.tool()
    def revision_planner(
        topics: list[str],
        scores: dict[str, float] = {},
        days_until_exam: int = 14,
        hours_per_day: float = 3.0,
    ) -> str:
        """
        Create a spaced-repetition revision schedule.

        Prioritizes weak topics (lower scores) and uses increasing
        intervals for stronger topics, optimizing review time.

        Args:
            topics: List of topic names to revise.
            scores: Dictionary mapping topic names to scores (0.0-1.0). Missing topics default to 0.5.
            days_until_exam: Number of days until the exam.
            hours_per_day: Hours available for revision daily.

        Returns:
            JSON string with the revision schedule.
        """
        if not topics:
            return json.dumps({"error": "No topics provided.", "success": False})

        # Assign default scores for missing topics
        topic_scores = {}
        for topic in topics:
            topic_scores[topic] = scores.get(topic, 0.5)

        # Sort topics by score (weakest first = most revision needed)
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1])

        # Calculate revision intervals based on scores
        # Lower score = shorter interval (more frequent review)
        revision_entries = []
        for topic, score in sorted_topics:
            if score < 0.3:
                interval = 1  # Review every day
                priority = "critical"
                sessions_needed = min(days_until_exam, 7)
            elif score < 0.5:
                interval = 2  # Every 2 days
                priority = "high"
                sessions_needed = min(days_until_exam // 2, 5)
            elif score < 0.7:
                interval = 3  # Every 3 days
                priority = "medium"
                sessions_needed = min(days_until_exam // 3, 4)
            else:
                interval = 5  # Every 5 days
                priority = "low"
                sessions_needed = min(days_until_exam // 5, 3)

            revision_entries.append({
                "topic": topic,
                "current_score": round(score * 100, 1),
                "priority": priority,
                "review_interval_days": interval,
                "total_sessions_planned": sessions_needed,
                "time_per_session_hours": round(hours_per_day / max(len(topics) * 0.3, 1), 1),
            })

        # Build day-by-day schedule
        today = datetime.now()
        schedule = []

        for day in range(1, days_until_exam + 1):
            date = today + timedelta(days=day)
            day_topics = []

            for entry in revision_entries:
                if day % entry["review_interval_days"] == 0:
                    day_topics.append({
                        "topic": entry["topic"],
                        "priority": entry["priority"],
                        "duration_hours": entry["time_per_session_hours"],
                        "activity": _get_revision_activity(entry["priority"]),
                    })

            if day_topics:
                schedule.append({
                    "day": day,
                    "date": date.strftime("%Y-%m-%d"),
                    "day_name": date.strftime("%A"),
                    "topics": day_topics,
                    "total_hours": round(sum(t["duration_hours"] for t in day_topics), 1),
                })

        result = {
            "success": True,
            "total_topics": len(topics),
            "days_until_exam": days_until_exam,
            "revision_priorities": revision_entries,
            "schedule": schedule,
            "strategies": [
                "🧠 Use active recall: Close your notes and try to remember",
                "📝 Write summary notes from memory after each revision session",
                "🔴 Focus extra time on critical and high-priority topics",
                "✅ Test yourself with practice problems after each revision",
                "😴 Get adequate sleep — memory consolidation happens during rest",
            ],
        }

        return json.dumps(result, indent=2)


def _get_revision_activity(priority: str) -> str:
    """Get recommended revision activity based on priority."""
    activities = {
        "critical": "Intensive review: re-read notes, solve problems, and practice active recall",
        "high": "Focused review: practice problems and summarize key concepts from memory",
        "medium": "Review key concepts and solve a few practice problems",
        "low": "Quick review: skim notes and verify understanding of main ideas",
    }
    return activities.get(priority, "General review and practice")
