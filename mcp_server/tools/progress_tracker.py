"""
StudyMate AI — Progress Tracker Tool.

Provides a comprehensive progress summary across all subjects and topics.
"""

import json


def register_tools(mcp) -> None:
    """Register progress tracker tools with the MCP server."""

    @mcp.tool()
    def progress_tracker(
        subjects: list[dict] = [],
        total_study_hours: float = 0,
        total_quizzes: int = 0,
        average_quiz_score: float = 0,
    ) -> str:
        """
        Generate a comprehensive progress summary.

        Compiles progress data across subjects and topics to provide
        an overview with visual indicators and milestone tracking.

        Args:
            subjects: List of subject dicts with 'name', 'topics_total', 'topics_completed', 'avg_score' keys.
            total_study_hours: Total hours studied across all subjects.
            total_quizzes: Total number of quizzes taken.
            average_quiz_score: Average quiz score (0-100).

        Returns:
            JSON string with progress summary and milestones.
        """
        subject_progress = []
        total_topics = 0
        completed_topics = 0

        for subj in subjects:
            name = subj.get("name", "Unknown")
            topics_total = subj.get("topics_total", 0)
            topics_completed = subj.get("topics_completed", 0)
            avg_score = subj.get("avg_score", 0)

            total_topics += topics_total
            completed_topics += topics_completed

            completion_pct = round(
                (topics_completed / max(topics_total, 1)) * 100, 1
            )

            # Visual progress bar
            filled = int(completion_pct / 10)
            bar = "█" * filled + "░" * (10 - filled)

            subject_progress.append({
                "subject": name,
                "topics_total": topics_total,
                "topics_completed": topics_completed,
                "completion_percentage": completion_pct,
                "progress_bar": f"[{bar}] {completion_pct}%",
                "average_score": round(avg_score, 1),
                "status": _get_status(completion_pct),
            })

        overall_completion = round(
            (completed_topics / max(total_topics, 1)) * 100, 1
        )

        # Milestone tracking
        milestones = _check_milestones(
            overall_completion, total_study_hours, total_quizzes, average_quiz_score
        )

        result = {
            "success": True,
            "overall_completion": overall_completion,
            "total_study_hours": round(total_study_hours, 1),
            "total_quizzes_taken": total_quizzes,
            "average_quiz_score": round(average_quiz_score, 1),
            "total_topics": total_topics,
            "topics_completed": completed_topics,
            "subject_progress": subject_progress,
            "milestones": milestones,
            "encouragement": _get_encouragement(overall_completion),
        }

        return json.dumps(result, indent=2)


def _get_status(completion: float) -> str:
    """Get status label based on completion percentage."""
    if completion >= 100:
        return "✅ Complete"
    elif completion >= 75:
        return "🏃 Almost there"
    elif completion >= 50:
        return "📚 Halfway"
    elif completion >= 25:
        return "🌱 Building momentum"
    else:
        return "🚀 Getting started"


def _check_milestones(completion: float, hours: float, quizzes: int, avg_score: float) -> list[dict]:
    """Check which milestones have been achieved."""
    milestones = [
        {"name": "First Steps", "description": "Start your study journey", "achieved": completion > 0, "icon": "👣"},
        {"name": "Quarter Done", "description": "Complete 25% of topics", "achieved": completion >= 25, "icon": "🎯"},
        {"name": "Halfway Hero", "description": "Complete 50% of topics", "achieved": completion >= 50, "icon": "⚡"},
        {"name": "Almost There", "description": "Complete 75% of topics", "achieved": completion >= 75, "icon": "🔥"},
        {"name": "All Complete", "description": "Complete all topics", "achieved": completion >= 100, "icon": "🏆"},
        {"name": "Quiz Master", "description": "Take 10+ quizzes", "achieved": quizzes >= 10, "icon": "📝"},
        {"name": "Study Marathon", "description": "Study for 20+ hours", "achieved": hours >= 20, "icon": "⏰"},
        {"name": "High Scorer", "description": "Average quiz score above 80%", "achieved": avg_score >= 80, "icon": "⭐"},
    ]
    return milestones


def _get_encouragement(completion: float) -> str:
    """Generate an encouraging message based on progress."""
    if completion >= 100:
        return "🎉 Outstanding! You've completed all your topics! Time to ace that exam!"
    elif completion >= 75:
        return "🔥 You're almost there! Keep pushing — the finish line is in sight!"
    elif completion >= 50:
        return "💪 Great progress! You're halfway done. Keep up the momentum!"
    elif completion >= 25:
        return "🌟 Nice work! You've built a solid foundation. Keep going!"
    else:
        return "🚀 Every journey starts with a single step. You've got this!"
