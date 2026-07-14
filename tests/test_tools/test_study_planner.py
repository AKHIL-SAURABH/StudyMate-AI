"""
StudyMate AI — Study Planner Tool Tests.

Unit tests for the study planner MCP tool.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
from datetime import datetime, timedelta


def test_study_planner_generates_plan():
    """Test that study planner generates a valid plan."""
    from mcp_server.tools.study_planner import register_tools

    class MockMCP:
        def __init__(self):
            self.tools = {}
        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator

    mock = MockMCP()
    register_tools(mock)

    planner = mock.tools["study_planner"]

    # Generate a plan
    exam_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    result_json = planner(
        subject="Mathematics",
        topics=["Algebra", "Calculus", "Geometry"],
        exam_date=exam_date,
        hours_per_day=3.0,
        difficulty_level="medium",
    )

    result = json.loads(result_json)
    assert result["success"] is True
    assert result["subject"] == "Mathematics"
    assert result["total_topics"] == 3
    assert len(result["plan"]) > 0
    assert len(result["tips"]) > 0


def test_study_planner_invalid_date():
    """Test study planner with invalid date format."""
    from mcp_server.tools.study_planner import register_tools

    class MockMCP:
        def __init__(self):
            self.tools = {}
        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator

    mock = MockMCP()
    register_tools(mock)

    planner = mock.tools["study_planner"]
    result = json.loads(planner(
        subject="Test",
        topics=["Topic1"],
        exam_date="invalid-date",
    ))

    assert result["success"] is False


def test_study_planner_empty_topics():
    """Test study planner with no topics."""
    from mcp_server.tools.study_planner import register_tools

    class MockMCP:
        def __init__(self):
            self.tools = {}
        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator

    mock = MockMCP()
    register_tools(mock)

    planner = mock.tools["study_planner"]
    result = json.loads(planner(
        subject="Test",
        topics=[],
        exam_date="2026-12-01",
    ))

    assert result["success"] is False


def test_quiz_generator():
    """Test that quiz generator creates valid questions."""
    from mcp_server.tools.quiz_generator import register_tools

    class MockMCP:
        def __init__(self):
            self.tools = {}
        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator

    mock = MockMCP()
    register_tools(mock)

    generator = mock.tools["quiz_generator"]
    result = json.loads(generator(
        topic="Python Programming",
        difficulty="easy",
        num_questions=3,
    ))

    assert result["success"] is True
    assert result["total_questions"] == 3
    assert len(result["questions"]) == 3

    for q in result["questions"]:
        assert "question" in q
        assert "options" in q
        assert "correct_answer" in q
        assert len(q["options"]) >= 2


def test_time_estimator():
    """Test time estimator tool."""
    from mcp_server.tools.time_estimator import register_tools

    class MockMCP:
        def __init__(self):
            self.tools = {}
        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator

    mock = MockMCP()
    register_tools(mock)

    estimator = mock.tools["time_estimator"]
    result = json.loads(estimator(
        topics=["Algebra", "Calculus"],
        difficulty="medium",
        current_knowledge={"Algebra": 0.6, "Calculus": 0.2},
    ))

    assert result["success"] is True
    assert result["total_estimated_hours"] > 0
    assert len(result["estimates"]) == 2
