"""
StudyMate AI — Authentication Service.

Handles user registration, login, and password management
using bcrypt for secure password hashing.
"""

import bcrypt

from backend.database import db
from backend.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from backend.models.user import UserCreate, UserLogin, UserResponse, UserInDB
from utils.helpers import generate_id, utc_now
from utils.logger import get_logger

logger = get_logger("auth_service")


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain-text password.

        Returns:
            Bcrypt hashed password string.
        """
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its bcrypt hash.

        Args:
            password: Plain-text password.
            password_hash: Stored bcrypt hash.

        Returns:
            True if password matches.
        """
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )

    async def register(self, data: UserCreate) -> UserResponse:
        """
        Register a new user.

        Args:
            data: User registration data.

        Returns:
            Created user response.

        Raises:
            UserAlreadyExistsError: If username or email already exists.
        """
        # Check for existing user
        existing = await db.execute_one(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (data.username, data.email),
        )
        if existing:
            raise UserAlreadyExistsError(data.username)

        user_id = generate_id()
        now = utc_now()
        password_hash = self.hash_password(data.password)

        await db.execute(
            """INSERT INTO users (id, username, email, password_hash, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, data.username, data.email, password_hash, now, now),
        )

        # Create default preferences for the user
        await db.execute(
            """INSERT INTO preferences (id, user_id, updated_at)
               VALUES (?, ?, ?)""",
            (generate_id(), user_id, now),
        )

        logger.info("User registered: %s (id=%s)", data.username, user_id)

        return UserResponse(
            id=user_id,
            username=data.username,
            email=data.email,
            created_at=now,
        )

    async def login(self, data: UserLogin) -> UserResponse:
        """
        Authenticate a user.

        Args:
            data: Login credentials.

        Returns:
            User response on successful authentication.

        Raises:
            AuthenticationError: If credentials are invalid.
        """
        user_row = await db.execute_one(
            "SELECT * FROM users WHERE username = ?",
            (data.username.lower(),),
        )

        if not user_row:
            # Also try email
            user_row = await db.execute_one(
                "SELECT * FROM users WHERE email = ?",
                (data.username.lower(),),
            )

        if not user_row:
            raise AuthenticationError("Invalid username or password")

        if not self.verify_password(data.password, user_row["password_hash"]):
            raise AuthenticationError("Invalid username or password")

        logger.info("User logged in: %s", user_row["username"])

        return UserResponse(
            id=user_row["id"],
            username=user_row["username"],
            email=user_row["email"],
            created_at=user_row["created_at"],
        )

    async def get_user(self, user_id: str) -> UserResponse:
        """
        Get user by ID.

        Args:
            user_id: User identifier.

        Returns:
            User response data.

        Raises:
            UserNotFoundError: If user doesn't exist.
        """
        user_row = await db.execute_one(
            "SELECT id, username, email, created_at FROM users WHERE id = ?",
            (user_id,),
        )

        if not user_row:
            raise UserNotFoundError(user_id)

        return UserResponse(**user_row)


# Singleton instance
auth_service = AuthService()
