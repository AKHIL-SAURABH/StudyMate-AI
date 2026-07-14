"""
StudyMate AI — Resource Finder Tool.

Recommends study resources based on topic and resource type preference.
"""

import json


def register_tools(mcp) -> None:
    """Register resource finder tools with the MCP server."""

    @mcp.tool()
    def resource_finder(
        topic: str,
        resource_type: str = "all",
        difficulty: str = "medium",
    ) -> str:
        """
        Find and recommend study resources for a given topic.

        Provides curated study resources including textbooks, videos,
        practice problems, and online courses categorized by type.

        Args:
            topic: The topic to find resources for.
            resource_type: Type of resource (textbook/video/practice/course/all).
            difficulty: Resource difficulty level (easy/medium/hard).

        Returns:
            JSON string with recommended resources organized by category.
        """
        resources = {
            "textbooks": [
                {
                    "title": f"Fundamentals of {topic}",
                    "type": "textbook",
                    "description": f"A comprehensive textbook covering all aspects of {topic} from basics to advanced concepts.",
                    "difficulty": "beginner-intermediate",
                    "recommendation": "Start here for a solid foundation",
                },
                {
                    "title": f"Advanced {topic}: Theory and Applications",
                    "type": "textbook",
                    "description": f"In-depth exploration of {topic} with practical examples and case studies.",
                    "difficulty": "intermediate-advanced",
                    "recommendation": "Great for deepening understanding after basics",
                },
            ],
            "videos": [
                {
                    "title": f"{topic} Crash Course",
                    "type": "video",
                    "description": f"Quick overview series covering key concepts in {topic}. Each video is 10-15 minutes.",
                    "difficulty": "beginner",
                    "recommendation": "Perfect for initial exposure and revision",
                },
                {
                    "title": f"{topic} — Full Lecture Series",
                    "type": "video",
                    "description": f"Complete university-level lecture series on {topic} with detailed explanations.",
                    "difficulty": "intermediate",
                    "recommendation": "Excellent for thorough understanding",
                },
                {
                    "title": f"Visual Guide to {topic}",
                    "type": "video",
                    "description": f"Animated explanations of complex {topic} concepts with visual demonstrations.",
                    "difficulty": "beginner-intermediate",
                    "recommendation": "Best for visual learners",
                },
            ],
            "practice": [
                {
                    "title": f"{topic} Practice Problem Set",
                    "type": "practice",
                    "description": f"Collection of 100+ practice problems covering all topics in {topic}, organized by difficulty.",
                    "difficulty": "all levels",
                    "recommendation": "Essential for exam preparation",
                },
                {
                    "title": f"{topic} Worked Examples",
                    "type": "practice",
                    "description": f"Step-by-step solutions to common {topic} problems with detailed explanations.",
                    "difficulty": "intermediate",
                    "recommendation": "Helps understand problem-solving approaches",
                },
            ],
            "courses": [
                {
                    "title": f"Introduction to {topic}",
                    "type": "course",
                    "description": f"Self-paced online course covering {topic} fundamentals with quizzes and assignments.",
                    "difficulty": "beginner",
                    "recommendation": "Good structured learning path for beginners",
                },
                {
                    "title": f"Mastering {topic}",
                    "type": "course",
                    "description": f"Advanced course on {topic} with projects, peer reviews, and certification.",
                    "difficulty": "advanced",
                    "recommendation": "For those ready to achieve mastery",
                },
            ],
        }

        # Filter by resource type
        if resource_type != "all":
            type_map = {
                "textbook": "textbooks",
                "video": "videos",
                "practice": "practice",
                "course": "courses",
            }
            key = type_map.get(resource_type, resource_type)
            filtered = {key: resources.get(key, [])}
        else:
            filtered = resources

        result = {
            "success": True,
            "topic": topic,
            "resource_type": resource_type,
            "resources": filtered,
            "study_tips": [
                f"📖 Start with foundational resources before moving to advanced {topic} material",
                "🎥 Use video resources for difficult concepts that need visual explanation",
                "✍️ Practice problems are essential — aim for at least 30 minutes of practice daily",
                "🔄 Alternate between different resource types to maintain engagement",
            ],
        }

        return json.dumps(result, indent=2)
