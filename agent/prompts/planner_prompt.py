"""
StudyMate AI — Planner Prompt.

Specialized prompt for generating structured study plans.
"""


PLANNER_PROMPT = """You are a study planning expert. Create a detailed, structured study plan based on the following information.

## Student Information
- **Subject**: {subject}
- **Topics**: {topics}
- **Exam Date**: {exam_date}
- **Available Hours/Day**: {hours_per_day}
- **Difficulty Level**: {difficulty}
- **Learning Style**: {learning_style}

## Requirements
1. Create a day-by-day schedule
2. Allocate time based on topic difficulty and importance
3. Include revision slots every 3-4 days
4. Add short breaks between study blocks
5. Include practice/quiz time for each topic
6. Be realistic about time allocation

## Format
Provide the plan in a clear, structured format that is easy to follow.
"""


def get_planner_prompt(
    subject: str,
    topics: str,
    exam_date: str,
    hours_per_day: float = 4.0,
    difficulty: str = "medium",
    learning_style: str = "visual",
) -> str:
    """
    Generate the planner prompt for study plan creation.

    Args:
        subject: Subject name.
        topics: Comma-separated topic list.
        exam_date: Exam date string.
        hours_per_day: Available study hours per day.
        difficulty: Subject difficulty level.
        learning_style: Student's learning style.

    Returns:
        Formatted planner prompt.
    """
    return PLANNER_PROMPT.format(
        subject=subject,
        topics=topics,
        exam_date=exam_date,
        hours_per_day=hours_per_day,
        difficulty=difficulty,
        learning_style=learning_style,
    )
