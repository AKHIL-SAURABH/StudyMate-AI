"""
StudyMate AI — Authentication Router.

Endpoints for user registration, login, and profile retrieval.
"""

from fastapi import APIRouter, Depends

from backend.dependencies import get_current_user_id
from backend.models.user import UserCreate, UserLogin
from backend.services.auth_service import auth_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=dict)
async def register(data: UserCreate) -> dict:
    """Register a new user account."""
    user = await auth_service.register(data)
    return {"success": True, "data": user.model_dump()}


@router.post("/login", response_model=dict)
async def login(data: UserLogin) -> dict:
    """Authenticate and login."""
    user = await auth_service.login(data)
    return {"success": True, "data": user.model_dump()}


@router.get("/me", response_model=dict)
async def get_current_user(user_id: str = Depends(get_current_user_id)) -> dict:
    """Get the current authenticated user's profile."""
    user = await auth_service.get_user(user_id)
    return {"success": True, "data": user.model_dump()}


from pydantic import BaseModel, Field

class PreferencesModel(BaseModel):
    study_hours_per_day: float = Field(default=4.0, ge=0.5, le=16.0)
    preferred_session_length: int = Field(default=45, ge=15, le=120)
    difficulty_preference: str = Field(default="medium")
    learning_style: str = Field(default="visual")


@router.get("/preferences", response_model=dict)
async def get_preferences(user_id: str = Depends(get_current_user_id)) -> dict:
    """Get the authenticated user's preferences."""
    from backend.database import db
    row = await db.execute_one(
        "SELECT study_hours_per_day, preferred_session_length, difficulty_preference, learning_style FROM preferences WHERE user_id = ?",
        (user_id,),
    )
    if not row:
        return {
            "success": True,
            "data": {
                "study_hours_per_day": 4.0,
                "preferred_session_length": 45,
                "difficulty_preference": "medium",
                "learning_style": "visual",
            }
        }
    return {"success": True, "data": dict(row)}


@router.post("/preferences", response_model=dict)
async def save_preferences(
    data: PreferencesModel,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Save user preferences."""
    from backend.database import db
    from utils.helpers import utc_now, generate_id
    
    now = utc_now()
    existing = await db.execute_one(
        "SELECT id FROM preferences WHERE user_id = ?",
        (user_id,),
    )
    
    if existing:
        await db.execute(
            """UPDATE preferences
               SET study_hours_per_day = ?, preferred_session_length = ?,
                   difficulty_preference = ?, learning_style = ?, updated_at = ?
               WHERE user_id = ?""",
            (
                data.study_hours_per_day,
                data.preferred_session_length,
                data.difficulty_preference.lower(),
                data.learning_style.lower(),
                now,
                user_id,
            ),
        )
    else:
        await db.execute(
            """INSERT INTO preferences (id, user_id, study_hours_per_day, preferred_session_length,
                                       difficulty_preference, learning_style, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                generate_id(),
                user_id,
                data.study_hours_per_day,
                data.preferred_session_length,
                data.difficulty_preference.lower(),
                data.learning_style.lower(),
                now,
            ),
        )
    return {"success": True, "message": "Preferences saved successfully"}
