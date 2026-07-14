"""
StudyMate AI — Quiz Router.

Endpoints for quiz generation, submission, and history.
"""

from fastapi import APIRouter, Depends

from backend.dependencies import get_current_user_id
from backend.models.quiz import QuizGenerateRequest, QuizSubmitRequest
from backend.services.quiz_service import quiz_service
from agent.controller import agent_controller
from utils.logger import get_logger

logger = get_logger("quiz_router")

router = APIRouter(prefix="/api/quiz", tags=["Quiz"])


@router.post("/generate", response_model=dict)
async def generate_quiz(
    data: QuizGenerateRequest,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """
    Generate a quiz on a topic.

    Uses the AI agent to call the quiz_generator MCP tool.
    """
    prompt = (
        f"Generate a {data.difficulty} difficulty quiz with {data.num_questions} "
        f"multiple-choice questions about '{data.topic}'. "
        f"Use the quiz_generator tool."
    )

    response = await agent_controller.process_message(
        user_id=user_id,
        message=prompt,
    )

    return {"success": True, "data": {"response": response.response, "agent_steps": [s.model_dump() for s in response.agent_steps]}}


@router.post("/submit", response_model=dict)
async def submit_quiz(
    data: QuizSubmitRequest,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Submit quiz answers and get score."""
    # Score the quiz
    quiz_questions = data.quiz_data.get("questions", [])
    correct = 0
    results = []

    for q in quiz_questions:
        q_num = str(q.get("question_number", ""))
        user_answer = data.answers.get(q_num, "")
        is_correct = user_answer == q.get("correct_answer", "")
        if is_correct:
            correct += 1

        results.append({
            "question_number": q_num,
            "user_answer": user_answer,
            "correct_answer": q.get("correct_answer", ""),
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })

    quiz_data_with_results = {**data.quiz_data, "results": results}

    score = await quiz_service.save_score(
        user_id=user_id,
        topic_id=data.topic_id,
        total_questions=len(quiz_questions),
        correct_answers=correct,
        quiz_data=quiz_data_with_results,
    )

    # Update progress if topic_id provided
    if data.topic_id:
        from backend.services.progress_service import progress_service
        confidence = correct / max(len(quiz_questions), 1)
        await progress_service.update_progress(user_id, data.topic_id, confidence)

    return {"success": True, "data": score.model_dump()}


@router.get("/history", response_model=dict)
async def get_quiz_history(
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Get quiz score history."""
    history = await quiz_service.get_history(user_id)
    return {"success": True, "data": [h.model_dump() for h in history]}
