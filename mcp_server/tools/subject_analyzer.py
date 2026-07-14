"""
StudyMate AI — Subject Analyzer Tool.

Provides deep analysis of subject coverage, depth, and gaps.
"""

import json


def register_tools(mcp) -> None:
    """Register subject analyzer tools with the MCP server."""

    @mcp.tool()
    def subject_analyzer(
        subject: str,
        topics: list[str],
        topic_scores: dict[str, float] = {},
        topic_hours: dict[str, float] = {},
    ) -> str:
        """
        Analyze the depth and breadth of study for a subject.

        Evaluates coverage across topics, identifies gaps, and provides
        a comprehensive subject readiness assessment.

        Args:
            subject: The subject name.
            topics: List of topic names within the subject.
            topic_scores: Dictionary mapping topic names to scores (0.0-1.0).
            topic_hours: Dictionary mapping topic names to hours studied.

        Returns:
            JSON string with subject analysis and readiness score.
        """
        if not topics:
            return json.dumps({"error": "No topics provided.", "success": False})

        # Analyze each topic
        topic_analysis = []
        total_score = 0
        total_hours = 0
        gaps = []
        strengths = []

        for topic in topics:
            score = topic_scores.get(topic, 0.0)
            hours = topic_hours.get(topic, 0.0)
            total_score += score
            total_hours += hours

            coverage = _assess_coverage(score, hours)

            entry = {
                "topic": topic,
                "score": round(score * 100, 1),
                "hours_studied": round(hours, 1),
                "coverage_level": coverage["level"],
                "coverage_icon": coverage["icon"],
                "depth_assessment": coverage["depth"],
            }
            topic_analysis.append(entry)

            if score < 0.4:
                gaps.append(topic)
            elif score >= 0.75:
                strengths.append(topic)

        # Overall readiness
        avg_score = total_score / len(topics)
        coverage_ratio = len([t for t in topics if topic_scores.get(t, 0) > 0]) / len(topics)
        readiness_score = round((avg_score * 0.6 + coverage_ratio * 0.4) * 100, 1)

        readiness_level = _get_readiness_level(readiness_score)

        result = {
            "success": True,
            "subject": subject,
            "total_topics": len(topics),
            "readiness_score": readiness_score,
            "readiness_level": readiness_level,
            "average_score": round(avg_score * 100, 1),
            "total_hours_studied": round(total_hours, 1),
            "coverage_ratio": round(coverage_ratio * 100, 1),
            "topic_analysis": topic_analysis,
            "knowledge_gaps": gaps,
            "strengths": strengths,
            "recommendations": _get_subject_recommendations(readiness_score, gaps, strengths, subject),
        }

        return json.dumps(result, indent=2)


def _assess_coverage(score: float, hours: float) -> dict:
    """Assess coverage level for a topic."""
    if score >= 0.8 and hours >= 3:
        return {"level": "thorough", "icon": "🟢", "depth": "Deep understanding demonstrated"}
    elif score >= 0.6 and hours >= 2:
        return {"level": "good", "icon": "🟡", "depth": "Solid understanding, some areas to reinforce"}
    elif score >= 0.3 and hours >= 1:
        return {"level": "partial", "icon": "🟠", "depth": "Basic understanding, needs more depth"}
    elif hours > 0:
        return {"level": "surface", "icon": "🔴", "depth": "Surface level — needs significantly more study"}
    else:
        return {"level": "not_covered", "icon": "⚫", "depth": "Not yet studied — start here"}


def _get_readiness_level(score: float) -> str:
    """Get readiness level description."""
    if score >= 85:
        return "🏆 Exam Ready — Well prepared for the exam"
    elif score >= 70:
        return "📗 Nearly Ready — Minor areas to address"
    elif score >= 50:
        return "📙 In Progress — Continue focused study"
    elif score >= 25:
        return "📕 Early Stage — Significant study needed"
    else:
        return "📓 Starting — Begin systematic study immediately"


def _get_subject_recommendations(score: float, gaps: list, strengths: list, subject: str) -> list[str]:
    """Generate subject-specific recommendations."""
    recs = []

    if gaps:
        recs.append(f"🎯 Priority: Focus on these gaps: {', '.join(gaps[:3])}")

    if score < 50:
        recs.append(f"📚 Dedicate at least 2 hours daily to {subject} until readiness improves")
        recs.append("📝 Create summary notes for each topic as you study them")
    elif score < 75:
        recs.append("🔄 Alternate between new topics and revision of weaker areas")
        recs.append("✍️ Take practice quizzes every 2-3 days to track progress")
    else:
        recs.append("⭐ Great preparation! Focus on maintaining knowledge with periodic review")
        recs.append("🧠 Try advanced problems and past exam questions")

    if strengths:
        recs.append(f"💪 Your strengths ({', '.join(strengths[:3])}) — use these as confidence boosters")

    return recs
