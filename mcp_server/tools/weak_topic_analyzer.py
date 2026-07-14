"""
StudyMate AI — Weak Topic Analyzer Tool.

Analyzes quiz scores and progress data to identify weak topics
and provide targeted improvement recommendations.
"""

import json


def register_tools(mcp) -> None:
    """Register weak topic analyzer tools with the MCP server."""

    @mcp.tool()
    def weak_topic_analyzer(
        topics: list[str],
        scores: dict[str, float] = {},
        study_hours: dict[str, float] = {},
    ) -> str:
        """
        Analyze quiz scores and study data to identify weak topics.

        Examines performance data across topics to find areas needing
        improvement and provides targeted recommendations.

        Args:
            topics: List of all topic names.
            scores: Dictionary mapping topic names to average scores (0.0-1.0).
            study_hours: Dictionary mapping topic names to hours studied.

        Returns:
            JSON string with weak topics analysis and recommendations.
        """
        if not topics:
            return json.dumps({"error": "No topics provided.", "success": False})

        analysis = []
        weak_topics = []
        strong_topics = []

        for topic in topics:
            score = scores.get(topic, 0.0)
            hours = study_hours.get(topic, 0.0)

            # Determine strength level
            if score < 0.3:
                level = "very_weak"
                color = "🔴"
            elif score < 0.5:
                level = "weak"
                color = "🟠"
            elif score < 0.7:
                level = "moderate"
                color = "🟡"
            elif score < 0.85:
                level = "strong"
                color = "🟢"
            else:
                level = "mastered"
                color = "⭐"

            # Calculate efficiency (score per hour studied)
            efficiency = round(score / max(hours, 0.5), 2) if hours > 0 else 0

            entry = {
                "topic": topic,
                "score_percentage": round(score * 100, 1),
                "hours_studied": round(hours, 1),
                "level": level,
                "indicator": color,
                "efficiency": efficiency,
                "recommendation": _get_recommendation(level, hours, topic),
            }
            analysis.append(entry)

            if level in ("very_weak", "weak"):
                weak_topics.append(entry)
            elif level in ("strong", "mastered"):
                strong_topics.append(entry)

        # Sort by score ascending (weakest first)
        analysis.sort(key=lambda x: x["score_percentage"])
        weak_topics.sort(key=lambda x: x["score_percentage"])

        # Generate overall insights
        avg_score = sum(scores.get(t, 0) for t in topics) / max(len(topics), 1)

        result = {
            "success": True,
            "total_topics_analyzed": len(topics),
            "weak_topics_count": len(weak_topics),
            "strong_topics_count": len(strong_topics),
            "average_score": round(avg_score * 100, 1),
            "analysis": analysis,
            "weak_topics": weak_topics,
            "strong_topics": [{"topic": t["topic"], "score": t["score_percentage"]} for t in strong_topics],
            "action_plan": [
                f"🎯 Focus primarily on your {len(weak_topics)} weak topic(s)",
                "📊 Increase practice problems for topics scoring below 50%",
                "🔄 Use the revision planner to schedule targeted review sessions",
                "📝 Take quizzes on weak topics every 2-3 days to track improvement",
                "💡 Consider different study methods if a topic isn't improving",
            ],
        }

        return json.dumps(result, indent=2)


def _get_recommendation(level: str, hours: float, topic: str) -> str:
    """Generate a specific recommendation based on performance level."""
    recommendations = {
        "very_weak": (
            f"Needs urgent attention. Start with the basics of {topic}. "
            f"{'Increase study time significantly — ' if hours < 2 else 'Try a different study approach — '}"
            f"use videos, tutoring, or worked examples."
        ),
        "weak": (
            f"Focus on fundamentals of {topic}. "
            f"Practice more problems and review mistakes carefully."
        ),
        "moderate": (
            f"Good foundation in {topic}. Push to strengthen with "
            f"challenging problems and timed practice."
        ),
        "strong": (
            f"Solid understanding of {topic}. "
            f"Maintain with periodic review and advanced problems."
        ),
        "mastered": (
            f"Excellent grasp of {topic}! "
            f"Light review sufficient. Consider helping peers to solidify knowledge."
        ),
    }
    return recommendations.get(level, f"Continue studying {topic} regularly.")
