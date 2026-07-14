"""
StudyMate AI — Time Estimator Tool.

Estimates the time needed to study each topic based on
difficulty, current knowledge level, and learning style.
"""

import json


def register_tools(mcp) -> None:
    """Register time estimator tools with the MCP server."""

    @mcp.tool()
    def time_estimator(
        topics: list[str],
        difficulty: str = "medium",
        current_knowledge: dict[str, float] = {},
        learning_style: str = "visual",
        target_score: float = 0.8,
    ) -> str:
        """
        Estimate the study time needed for each topic.

        Calculates personalized time estimates considering difficulty,
        current knowledge level, and learning style preferences.

        Args:
            topics: List of topic names to estimate.
            difficulty: Overall difficulty level (easy/medium/hard).
            current_knowledge: Dict mapping topic names to knowledge level (0.0-1.0).
            learning_style: Preferred learning style (visual/auditory/reading/kinesthetic).
            target_score: Target knowledge level to achieve (0.0-1.0).

        Returns:
            JSON string with time estimates per topic and total.
        """
        if not topics:
            return json.dumps({"error": "No topics provided.", "success": False})

        # Base hours per topic by difficulty
        base_hours = {"easy": 2.0, "medium": 4.0, "hard": 6.0}
        base = base_hours.get(difficulty, 4.0)

        # Learning style multiplier
        style_multipliers = {
            "visual": 1.0,
            "auditory": 1.1,
            "reading": 0.9,
            "kinesthetic": 1.2,
        }
        style_mult = style_multipliers.get(learning_style, 1.0)

        estimates = []
        total_hours = 0

        for topic in topics:
            knowledge = current_knowledge.get(topic, 0.0)

            # Knowledge gap determines effort
            gap = max(target_score - knowledge, 0)
            knowledge_multiplier = gap / target_score if target_score > 0 else 1.0

            # Calculate estimated hours
            estimated_hours = round(base * knowledge_multiplier * style_mult, 1)
            estimated_hours = max(estimated_hours, 0.5)  # Minimum 30 minutes

            # Breakdown by activity
            breakdown = {
                "reading_notes": round(estimated_hours * 0.3, 1),
                "practice_problems": round(estimated_hours * 0.35, 1),
                "review_revision": round(estimated_hours * 0.2, 1),
                "self_testing": round(estimated_hours * 0.15, 1),
            }

            # Recommended sessions
            sessions_needed = max(1, int(estimated_hours / 1.5))  # 1.5-hour sessions

            estimates.append({
                "topic": topic,
                "current_knowledge": round(knowledge * 100, 1),
                "knowledge_gap": round(gap * 100, 1),
                "estimated_hours": estimated_hours,
                "sessions_needed": sessions_needed,
                "session_length_minutes": 90,
                "time_breakdown": breakdown,
                "priority": _get_priority(gap),
            })

            total_hours += estimated_hours

        # Sort by priority (largest gap first)
        estimates.sort(key=lambda x: x["knowledge_gap"], reverse=True)

        # Study schedule recommendation
        if total_hours <= 10:
            schedule_recommendation = "With focused study, you can complete this in 3-5 days"
        elif total_hours <= 30:
            schedule_recommendation = "Plan for 1-2 weeks of consistent study"
        elif total_hours <= 60:
            schedule_recommendation = "This requires 2-4 weeks of dedicated study"
        else:
            schedule_recommendation = "Budget at least a month for thorough preparation"

        result = {
            "success": True,
            "total_estimated_hours": round(total_hours, 1),
            "total_topics": len(topics),
            "difficulty": difficulty,
            "learning_style": learning_style,
            "target_score": round(target_score * 100, 1),
            "schedule_recommendation": schedule_recommendation,
            "estimates": estimates,
            "optimization_tips": [
                "🎯 Start with the highest priority (biggest gap) topics",
                "⏰ Use 90-minute study blocks with 15-minute breaks",
                "📝 Spend 35% of time on practice problems for best retention",
                "🔄 Review previous topics briefly before starting new ones",
                f"🧠 As a {learning_style} learner, prioritize {_get_style_tip(learning_style)}",
            ],
        }

        return json.dumps(result, indent=2)


def _get_priority(gap: float) -> str:
    """Determine study priority based on knowledge gap."""
    if gap > 0.7:
        return "🔴 Critical"
    elif gap > 0.5:
        return "🟠 High"
    elif gap > 0.3:
        return "🟡 Medium"
    else:
        return "🟢 Low"


def _get_style_tip(style: str) -> str:
    """Get learning style-specific tip."""
    tips = {
        "visual": "diagrams, flowcharts, and color-coded notes",
        "auditory": "recorded explanations, discussions, and reading aloud",
        "reading": "detailed notes, textbooks, and written summaries",
        "kinesthetic": "hands-on practice, problem-solving, and teaching others",
    }
    return tips.get(style, "varied study methods")
