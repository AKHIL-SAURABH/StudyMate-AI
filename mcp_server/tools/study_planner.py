"""
StudyMate AI — Study Planner Tool.

Generates personalized, day-by-day study plans based on
subjects, topics, exam date, and available study hours.
"""

import json
from datetime import datetime, timedelta
from typing import Optional


def register_tools(mcp) -> None:
    """Register study planner tools with the MCP server."""

    @mcp.tool()
    def study_planner(
        subject: str,
        topics: list[str],
        exam_date: str,
        hours_per_day: float = 4.0,
        difficulty_level: str = "medium",
    ) -> str:
        """
        Generate a personalized day-by-day study plan.

        Creates an optimized study schedule that distributes topics across
        available days, accounting for difficulty and revision time.

        Args:
            subject: The subject name (e.g., 'Mathematics').
            topics: List of topic names to cover.
            exam_date: Exam date in YYYY-MM-DD format.
            hours_per_day: Available study hours per day (default: 4.0).
            difficulty_level: Overall difficulty (easy/medium/hard).

        Returns:
            JSON string with the day-by-day study plan.
        """
        try:
            exam = datetime.strptime(exam_date, "%Y-%m-%d")
        except ValueError:
            return json.dumps({
                "error": "Invalid date format. Use YYYY-MM-DD.",
                "success": False,
            })

        today = datetime.now()
        days_remaining = max((exam - today).days, 1)

        if not topics:
            return json.dumps({
                "error": "No topics provided.",
                "success": False,
            })

        # Difficulty multiplier for time allocation
        difficulty_multipliers = {"easy": 0.8, "medium": 1.0, "hard": 1.3}
        multiplier = difficulty_multipliers.get(difficulty_level, 1.0)

        # Calculate hours per topic
        total_hours = days_remaining * hours_per_day
        # Reserve 20% for revision
        study_hours = total_hours * 0.8
        revision_hours = total_hours * 0.2

        hours_per_topic = (study_hours / len(topics)) * multiplier

        # Build day-by-day plan
        plan = []
        current_date = today
        topic_index = 0
        topic_hours_remaining = hours_per_topic
        revision_topics = []

        for day_num in range(1, days_remaining + 1):
            current_date = today + timedelta(days=day_num - 1)
            day_plan = {
                "day": day_num,
                "date": current_date.strftime("%Y-%m-%d"),
                "day_name": current_date.strftime("%A"),
                "tasks": [],
                "total_hours": 0,
            }

            remaining_hours = hours_per_day

            # Revision day every 4th day
            if day_num % 4 == 0 and revision_topics:
                rev_time = min(remaining_hours * 0.4, 2.0)
                day_plan["tasks"].append({
                    "type": "revision",
                    "topics": revision_topics[-3:],
                    "duration_hours": round(rev_time, 1),
                    "activity": "Review and practice problems",
                })
                remaining_hours -= rev_time

            # New topic study
            while remaining_hours > 0.5 and topic_index < len(topics):
                study_time = min(remaining_hours, topic_hours_remaining)
                topic_name = topics[topic_index]

                day_plan["tasks"].append({
                    "type": "study",
                    "topic": topic_name,
                    "duration_hours": round(study_time, 1),
                    "activity": f"Study {topic_name} — focus on key concepts and practice",
                })

                remaining_hours -= study_time
                topic_hours_remaining -= study_time

                if topic_hours_remaining <= 0.1:
                    revision_topics.append(topic_name)
                    topic_index += 1
                    topic_hours_remaining = hours_per_topic

            day_plan["total_hours"] = round(hours_per_day - remaining_hours, 1)
            if day_plan["tasks"]:
                plan.append(day_plan)

        result = {
            "success": True,
            "subject": subject,
            "exam_date": exam_date,
            "days_remaining": days_remaining,
            "total_topics": len(topics),
            "hours_per_day": hours_per_day,
            "difficulty": difficulty_level,
            "plan": plan[:days_remaining],
            "tips": [
                "🎯 Focus on understanding concepts, not just memorization",
                "📝 Take short notes after each study session",
                "🔄 Revise previous topics every 4th day",
                "⏰ Take a 10-minute break every 45 minutes",
                "💪 Stay consistent — even 30 minutes daily helps",
            ],
        }

        return json.dumps(result, indent=2)
