"""
StudyMate AI — Analytics Router.

Endpoints for study analytics and weekly summaries.
"""

from fastapi import APIRouter, Depends

from backend.dependencies import get_current_user_id
from backend.services.analytics_service import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/", response_model=dict)
async def get_analytics(
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Get comprehensive study analytics."""
    analytics = await analytics_service.get_analytics(user_id)
    return {"success": True, "data": analytics.model_dump()}


@router.get("/weekly", response_model=dict)
async def get_weekly_summary(
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Get this week's study summary."""
    summary = await analytics_service.get_weekly_summary(user_id)
    return {"success": True, "data": summary.model_dump()}
