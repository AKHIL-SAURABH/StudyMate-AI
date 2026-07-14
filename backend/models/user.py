"""
StudyMate AI — User Pydantic Models.

Defines request/response schemas for user authentication and profile operations.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class UserCreate(BaseModel):
    """Schema for user registration."""

    username: str = Field(
        ..., min_length=3, max_length=50,
        description="Unique username (3-50 chars, alphanumeric + underscores)"
    )
    email: str = Field(
        ..., max_length=255,
        description="Valid email address"
    )
    password: str = Field(
        ..., min_length=6, max_length=128,
        description="Password (minimum 6 characters)"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Ensure username contains only safe characters."""
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must contain only letters, numbers, and underscores")
        return v.lower()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email format validation."""
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid email format")
        return v.lower()


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Account password")


class UserResponse(BaseModel):
    """Schema for user data in API responses."""

    id: str
    username: str
    email: str
    created_at: str

    model_config = {"from_attributes": True}


class UserInDB(BaseModel):
    """Internal user representation with hashed password."""

    id: str
    username: str
    email: str
    password_hash: str
    created_at: str
    updated_at: str
