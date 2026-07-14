"""
StudyMate AI — Progress Router.

Endpoints for progress tracking and updates.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.dependencies import get_current_user_id
from backend.services.progress_service import progress_service

router = APIRouter(prefix="/api/progress", tags=["Progress"])


class ProgressUpdateRequest(BaseModel):
    """Schema for updating topic progress."""
    topic_id: str = Field(..., description="Topic identifier")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence level")


@router.get("/", response_model=dict)
async def get_progress(
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Get progress overview for the current user."""
    overview = await progress_service.get_overview(user_id)
    return {"success": True, "data": overview.model_dump()}


@router.post("/update", response_model=dict)
async def update_progress(
    data: ProgressUpdateRequest,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Update progress for a topic."""
    await progress_service.update_progress(
        user_id=user_id,
        topic_id=data.topic_id,
        confidence_score=data.confidence_score,
    )
    return {"success": True, "message": "Progress updated"}
