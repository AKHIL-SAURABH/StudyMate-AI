"""
StudyMate AI — Subjects Router.

Endpoints for subject and topic CRUD operations.
"""

from fastapi import APIRouter, Depends

from backend.dependencies import get_current_user_id
from backend.models.subject import SubjectCreate, TopicCreate
from backend.services.subject_service import subject_service

router = APIRouter(prefix="/api/subjects", tags=["Subjects"])


@router.post("/", response_model=dict)
async def create_subject(
    data: SubjectCreate,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Create a new subject."""
    subject = await subject_service.create_subject(user_id, data)
    return {"success": True, "data": subject.model_dump()}


@router.get("/", response_model=dict)
async def get_subjects(
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Get all subjects for the current user."""
    subjects = await subject_service.get_subjects(user_id)
    return {"success": True, "data": [s.model_dump() for s in subjects]}


@router.get("/{subject_id}", response_model=dict)
async def get_subject(subject_id: str) -> dict:
    """Get a single subject with its topics."""
    subject = await subject_service.get_subject(subject_id)
    return {"success": True, "data": subject.model_dump()}


@router.post("/{subject_id}/topics", response_model=dict)
async def create_topic(subject_id: str, data: TopicCreate) -> dict:
    """Create a new topic under a subject."""
    topic = await subject_service.create_topic(subject_id, data)
    return {"success": True, "data": topic.model_dump()}


@router.get("/{subject_id}/topics", response_model=dict)
async def get_topics(subject_id: str) -> dict:
    """Get all topics for a subject."""
    topics = await subject_service.get_topics(subject_id)
    return {"success": True, "data": [t.model_dump() for t in topics]}


@router.delete("/{subject_id}", response_model=dict)
async def delete_subject(subject_id: str) -> dict:
    """Delete a subject and all its topics."""
    await subject_service.delete_subject(subject_id)
    return {"success": True, "message": "Subject deleted"}


@router.delete("/topics/{topic_id}", response_model=dict)
async def delete_topic(topic_id: str) -> dict:
    """Delete a topic by ID."""
    await subject_service.delete_topic(topic_id)
    return {"success": True, "message": "Topic deleted"}


from backend.models.session import StudySessionCreate
from backend.services.session_service import session_service

@router.post("/sessions", response_model=dict)
async def log_study_session(
    data: StudySessionCreate,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Log a new study session."""
    session = await session_service.create_session(user_id, data)
    return {"success": True, "data": session.model_dump()}
