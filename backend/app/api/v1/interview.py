from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services import interview_service
from app.models import InterviewSession
from app.schemas import (
    MockInterviewStartRequest,
    MockInterviewEvaluateRequest,
    MockInterviewSummaryRequest,
    InterviewSessionResponse,
    InterviewSessionDetailResponse,
)
import json

router = APIRouter()


@router.post("/start")
async def start_interview(request: MockInterviewStartRequest):
    questions = await interview_service.start_interview(
        request.position, request.question_count
    )
    return {"questions": questions}


@router.post("/evaluate")
async def evaluate_answer(request: MockInterviewEvaluateRequest):
    result = await interview_service.evaluate_answer(
        request.question,
        request.user_answer,
        request.question_index,
        request.total_score,
    )
    return result


@router.post("/summary")
async def generate_summary(request: MockInterviewSummaryRequest):
    result = await interview_service.generate_summary(
        request.position,
        request.answers,
        request.total_score,
        request.question_count,
    )
    return result


@router.post("/save")
async def save_interview_session(
    request: dict,
    db: Session = Depends(get_db),
):
    session = InterviewSession(
        position=request.get("position"),
        questions_json=json.dumps(request.get("questions", []), ensure_ascii=False),
        answers_json=json.dumps(request.get("answers", {}), ensure_ascii=False),
        score=request.get("score"),
        feedback=request.get("feedback"),
        duration=request.get("duration"),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"id": session.id}


@router.get("/sessions", response_model=List[InterviewSessionResponse])
def get_interview_sessions(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(InterviewSession)
        .order_by(InterviewSession.created_at.desc())
        .limit(limit)
        .all()
    )
    return sessions


@router.get("/sessions/{session_id}", response_model=InterviewSessionDetailResponse)
def get_interview_detail(
    session_id: int,
    db: Session = Depends(get_db),
):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="会话不存在")
    return {
        "id": session.id,
        "position": session.position,
        "score": session.score,
        "created_at": session.created_at,
        "questions": json.loads(session.questions_json or "[]"),
        "answers": json.loads(session.answers_json or "{}"),
        "feedback": session.feedback,
        "duration": session.duration,
    }
