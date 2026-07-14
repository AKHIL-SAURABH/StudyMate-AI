"""
StudyMate AI — Subject API Tests.

Tests for subject and topic CRUD endpoints.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.database import db


@pytest.fixture(autouse=True)
async def setup_db():
    """Initialize test database."""
    await db.initialize()
    yield


@pytest.fixture
async def auth_user():
    """Create and return a test user with headers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        result = await client.post("/api/auth/register", json={
            "username": "test_subj_user",
            "email": "test_subj@example.com",
            "password": "testpass123",
        })
        data = result.json()

        # If user already exists, login instead
        if not data.get("success"):
            result = await client.post("/api/auth/login", json={
                "username": "test_subj_user",
                "password": "testpass123",
            })
            data = result.json()

    user_id = data["data"]["id"]
    return {"X-User-ID": user_id}


@pytest.mark.asyncio
async def test_create_subject(auth_user):
    """Test creating a subject."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/subjects/",
            json={"name": "Mathematics", "description": "Math course", "difficulty_level": "medium"},
            headers=auth_user,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Mathematics"


@pytest.mark.asyncio
async def test_get_subjects(auth_user):
    """Test getting all subjects."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/subjects/", headers=auth_user)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_create_topic(auth_user):
    """Test creating a topic under a subject."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create subject first
        subj_result = await client.post(
            "/api/subjects/",
            json={"name": "Physics Test", "description": "For testing"},
            headers=auth_user,
        )
        subject_id = subj_result.json()["data"]["id"]

        # Create topic
        response = await client.post(
            f"/api/subjects/{subject_id}/topics",
            json={"name": "Kinematics", "priority": 5},
            headers=auth_user,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Kinematics"
    assert data["data"]["priority"] == 5
