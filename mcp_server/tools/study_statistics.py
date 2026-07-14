"""
StudyMate AI — Study Statistics Tool.

Computes study analytics and patterns over configurable time periods.
"""

import json
from datetime import datetime, timedelta


def register_tools(mcp) -> None:
    """Register study statistics tools with the MCP server."""

    @mcp.tool()
    def study_statistics(
        study_sessions: list[dict] = [],
        quiz_scores: list[dict] = [],
        period: str = "week",
    ) -> str:
        """
        Generate study statistics and patterns.

        Analyzes study session data and quiz performance to provide
        insights about study habits and productivity.

        Args:
            study_sessions: List of session dicts with 'date', 'duration_minutes', 'topic' keys.
            quiz_scores: List of quiz dicts with 'date', 'score', 'topic' keys.
            period: Analysis period (day/week/month/all).

        Returns:
            JSON string with computed statistics and insights.
        """
        total_minutes = sum(s.get("duration_minutes", 0) for s in study_sessions)
        total_sessions = len(study_sessions)
        avg_session = round(total_minutes / max(total_sessions, 1), 1)

        # Quiz statistics
        quiz_total = len(quiz_scores)
        avg_quiz_score = 0
        if quiz_scores:
            avg_quiz_score = round(
                sum(q.get("score", 0) for q in quiz_scores) / quiz_total, 1
            )

        # Topics studied
        topics = set()
        for s in study_sessions:
            if s.get("topic"):
                topics.add(s["topic"])

        # Study distribution by topic
        topic_minutes = {}
        for s in study_sessions:
            topic = s.get("topic", "General")
            topic_minutes[topic] = topic_minutes.get(topic, 0) + s.get("duration_minutes", 0)

        topic_distribution = [
            {
                "topic": topic,
                "minutes": minutes,
                "hours": round(minutes / 60, 1),
                "percentage": round(minutes / max(total_minutes, 1) * 100, 1),
            }
            for topic, minutes in sorted(topic_minutes.items(), key=lambda x: x[1], reverse=True)
        ]

        # Performance trend
        trend = "stable"
        if len(quiz_scores) >= 3:
            recent = [q["score"] for q in quiz_scores[-3:]]
            older = [q["score"] for q in quiz_scores[:3]]
            if sum(recent) / 3 > sum(older) / 3 + 5:
                trend = "improving"
            elif sum(recent) / 3 < sum(older) / 3 - 5:
                trend = "declining"

        # Productivity insights
        insights = _generate_insights(
            total_minutes, avg_session, avg_quiz_score, trend, total_sessions
        )

        result = {
            "success": True,
            "period": period,
            "summary": {
                "total_study_minutes": total_minutes,
                "total_study_hours": round(total_minutes / 60, 1),
                "total_sessions": total_sessions,
                "average_session_minutes": avg_session,
                "unique_topics_studied": len(topics),
                "total_quizzes": quiz_total,
                "average_quiz_score": avg_quiz_score,
                "performance_trend": trend,
            },
            "topic_distribution": topic_distribution,
            "insights": insights,
        }

        return json.dumps(result, indent=2)


def _generate_insights(
    minutes: int, avg_session: float, avg_score: float, trend: str, sessions: int
) -> list[str]:
    """Generate personalized insights from study data."""
    insights = []

    hours = minutes / 60

    if hours < 5:
        insights.append("📈 Consider increasing study time to at least 1 hour per day for better results")
    elif hours > 30:
        insights.append("🌟 Impressive study commitment! Make sure to balance with rest")

    if avg_session < 20:
        insights.append("⏰ Your sessions are quite short. Try 30-45 minute focused blocks")
    elif avg_session > 90:
        insights.append("⚠️ Long sessions can reduce focus. Consider breaking into 45-minute blocks with breaks")

    if avg_score < 50:
        insights.append("📖 Quiz scores suggest more review is needed. Focus on understanding core concepts")
    elif avg_score > 80:
        insights.append("⭐ Great quiz performance! Challenge yourself with harder material")

    if trend == "improving":
        insights.append("📈 Your performance is trending upward! Your study strategy is working")
    elif trend == "declining":
        insights.append("📉 Performance is dipping. Consider changing your study approach or getting more rest")

    if sessions == 0:
        insights.append("🚀 Log your first study session to start tracking your progress!")

    return insights
