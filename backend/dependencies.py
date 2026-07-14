"""
StudyMate AI — FastAPI Dependencies.

Provides dependency injection functions for database access,
authentication, and common request handling.
"""

from typing import Optional

from fastapi import Header, HTTPException

from backend.database import db, Database
from utils.logger import get_logger

logger = get_logger("dependencies")


async def get_database() -> Database:
    """
    Dependency that provides the database instance.

    Returns:
        Initialized Database instance.
    """
    return db


async def get_current_user_id(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
) -> str:
    """
    Dependency that extracts and validates the user ID from request headers.

    For simplicity, the Streamlit frontend sends the user ID in a header
    after login. In production, this would validate a JWT token.

    Args:
        x_user_id: User ID from the X-User-ID request header.

    Returns:
        Validated user ID string.

    Raises:
        HTTPException: If no user ID is provided.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail={"code": "AUTH_ERROR", "message": "Missing X-User-ID header"},
        )

    # Verify user exists in database
    user = await db.execute_one(
        "SELECT id FROM users WHERE id = ?", (x_user_id,)
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail={"code": "AUTH_ERROR", "message": "Invalid user ID"},
        )

    return x_user_id
