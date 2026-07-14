"""
StudyMate AI — Motivation Generator Tool.

Generates motivational content, study tips, and streak information.
"""

import json
import random


def register_tools(mcp) -> None:
    """Register motivation generator tools with the MCP server."""

    @mcp.tool()
    def motivation_generator(
        current_streak: int = 0,
        total_study_hours: float = 0,
        recent_score: float = 0,
        context: str = "general",
    ) -> str:
        """
        Generate motivational content tailored to the student's context.

        Provides encouraging messages, study tips, and streak
        information to keep students motivated.

        Args:
            current_streak: Current study streak in days.
            total_study_hours: Total hours studied overall.
            recent_score: Most recent quiz score (0-100).
            context: Context for motivation (general/low_score/high_score/streak/tired).

        Returns:
            JSON string with motivational message and study tips.
        """
        message = _get_motivational_message(context, current_streak, recent_score)
        quote = _get_random_quote()
        tips = _get_study_tips(context)

        streak_info = {
            "current_streak_days": current_streak,
            "streak_message": _get_streak_message(current_streak),
            "next_milestone": _get_next_streak_milestone(current_streak),
        }

        achievements = _check_achievements(current_streak, total_study_hours, recent_score)

        result = {
            "success": True,
            "motivational_message": message,
            "quote": quote,
            "streak_info": streak_info,
            "study_tips": tips,
            "achievements_unlocked": achievements,
            "reminder": "Remember: consistency beats intensity. Even 20 minutes of focused study counts! 💪",
        }

        return json.dumps(result, indent=2)


def _get_motivational_message(context: str, streak: int, score: float) -> str:
    """Generate context-appropriate motivational message."""
    messages = {
        "general": [
            "Every study session brings you one step closer to your goal! 🌟",
            "You're investing in your future — that's the smartest thing you can do! 📚",
            "Knowledge is the one treasure that grows when shared. Keep learning! 💡",
        ],
        "low_score": [
            "A low score isn't failure — it's a roadmap showing you what to focus on next! 🗺️",
            "Every expert was once a beginner. Don't give up — review, practice, and try again! 💪",
            "Mistakes are proof that you're trying. Let's turn this into a learning opportunity! 🔄",
        ],
        "high_score": [
            "Incredible score! Your hard work is paying off beautifully! 🏆",
            "You're on fire! This level of dedication will take you far! 🔥",
            "Outstanding performance! Keep this momentum going! ⭐",
        ],
        "streak": [
            f"{'Amazing' if streak >= 7 else 'Great'} — {streak} day streak! Consistency is your superpower! 🔥",
            f"Day {streak} of your learning journey! Each day builds on the last! 📈",
            f"Your {streak}-day streak proves your commitment. You're unstoppable! 💫",
        ],
        "tired": [
            "It's okay to take a short break. Rest is part of the learning process! 😌",
            "A 10-minute walk can refresh your mind better than another hour of studying. 🚶",
            "Even a brief review session today keeps your streak alive. Quality over quantity! 🌿",
        ],
    }

    context_messages = messages.get(context, messages["general"])
    return random.choice(context_messages)


def _get_random_quote() -> dict:
    """Return a random inspirational quote about learning."""
    quotes = [
        {"text": "Education is the most powerful weapon which you can use to change the world.", "author": "Nelson Mandela"},
        {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
        {"text": "It does not matter how slowly you go as long as you do not stop.", "author": "Confucius"},
        {"text": "The beautiful thing about learning is that no one can take it away from you.", "author": "B.B. King"},
        {"text": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
        {"text": "The expert in anything was once a beginner.", "author": "Helen Hayes"},
        {"text": "Perseverance is not a long race; it is many short races one after the other.", "author": "Walter Elliot"},
        {"text": "The secret of getting ahead is getting started.", "author": "Mark Twain"},
    ]
    return random.choice(quotes)


def _get_study_tips(context: str) -> list[str]:
    """Get study tips relevant to the context."""
    tips = {
        "general": [
            "🕐 Study in 25-minute focused blocks (Pomodoro Technique)",
            "📝 Summarize what you learned in your own words after each session",
            "🧠 Use active recall — test yourself instead of re-reading notes",
        ],
        "low_score": [
            "📖 Go back to the basics — make sure your foundation is solid",
            "✍️ Write down every mistake and review them before the next quiz",
            "👥 Try explaining the topic to someone else — teaching reinforces learning",
        ],
        "high_score": [
            "🎯 Challenge yourself with harder problems to keep growing",
            "🤝 Help classmates who are struggling — teaching deepens understanding",
            "📊 Track your progress patterns to optimize your study routine",
        ],
        "tired": [
            "😴 Get 7-8 hours of sleep — your brain consolidates memories during rest",
            "🚰 Stay hydrated and eat brain-healthy snacks",
            "🧘 Try a 5-minute breathing exercise to reset your focus",
        ],
    }
    return tips.get(context, tips["general"])


def _get_streak_message(streak: int) -> str:
    """Generate streak-specific message."""
    if streak == 0:
        return "Start your streak today! Study for just 15 minutes to begin! 🌱"
    elif streak < 3:
        return f"Nice start! {streak} day(s) in. Build this into a habit! 🌿"
    elif streak < 7:
        return f"{streak} days strong! You're building a great habit! 💪"
    elif streak < 14:
        return f"Wow, {streak} days! You're on a roll! Keep it going! 🔥"
    elif streak < 30:
        return f"Incredible {streak}-day streak! You're unstoppable! ⚡"
    else:
        return f"LEGENDARY {streak}-day streak! You're an absolute champion! 🏆"


def _get_next_streak_milestone(streak: int) -> dict:
    """Get the next streak milestone."""
    milestones = [3, 7, 14, 21, 30, 60, 90, 100, 365]
    for m in milestones:
        if streak < m:
            return {"days_needed": m - streak, "milestone": f"{m}-day streak", "reward": f"🏅 {m}-Day Warrior badge"}
    return {"days_needed": 0, "milestone": "All milestones achieved!", "reward": "🏆 Ultimate Scholar"}


def _check_achievements(streak: int, hours: float, score: float) -> list[str]:
    """Check recently unlocked achievements."""
    achievements = []
    if streak >= 7:
        achievements.append("🔥 Week Warrior — 7-day study streak")
    if streak >= 30:
        achievements.append("⚡ Month Master — 30-day study streak")
    if hours >= 10:
        achievements.append("⏰ Dedicated Student — 10+ hours studied")
    if hours >= 50:
        achievements.append("📚 Study Champion — 50+ hours studied")
    if score >= 90:
        achievements.append("⭐ Quiz Star — Scored 90%+ on a quiz")
    if score >= 100:
        achievements.append("🏆 Perfect Score — Scored 100% on a quiz")
    return achievements
