"""
StudyMate AI — Auth API Tests.

Tests for user registration, login, and profile endpoints.
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
    """Initialize the test database before each test."""
    await db.initialize()
    yield
    # Clean up test data
    await db.execute("DELETE FROM users WHERE username LIKE 'test_%'")


@pytest.mark.asyncio
async def test_register_user():
    """Test user registration endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/auth/register", json={
            "username": "test_user_reg",
            "email": "test_reg@example.com",
            "password": "testpass123",
        })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == "test_user_reg"
    assert "id" in data["data"]


@pytest.mark.asyncio
async def test_register_duplicate_user():
    """Test that duplicate registration fails."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First registration
        await client.post("/api/auth/register", json={
            "username": "test_user_dup",
            "email": "test_dup@example.com",
            "password": "testpass123",
        })

        # Duplicate
        response = await client.post("/api/auth/register", json={
            "username": "test_user_dup",
            "email": "test_dup2@example.com",
            "password": "testpass123",
        })

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success():
    """Test successful login."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register first
        await client.post("/api/auth/register", json={
            "username": "test_user_login",
            "email": "test_login@example.com",
            "password": "testpass123",
        })

        # Login
        response = await client.post("/api/auth/login", json={
            "username": "test_user_login",
            "password": "testpass123",
        })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == "test_user_login"


@pytest.mark.asyncio
async def test_login_wrong_password():
    """Test login with wrong password."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/auth/register", json={
            "username": "test_user_wrongpw",
            "email": "test_wrongpw@example.com",
            "password": "testpass123",
        })

        response = await client.post("/api/auth/login", json={
            "username": "test_user_wrongpw",
            "password": "wrongpassword",
        })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_unauthorized():
    """Test accessing /me without user ID header."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
