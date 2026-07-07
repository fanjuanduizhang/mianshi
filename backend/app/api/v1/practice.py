from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services import practice_service
from app.models import QuestionRecord
from app.schemas import (
    QuestionItem,
    PracticeCheckRequest,
    PracticeCheckResponse,
    QuestionRecordResponse,
)
from datetime import datetime

router = APIRouter()


@router.get("/categories")
def get_categories():
    return {"categories": practice_service.get_categories()}


@router.get("/questions", response_model=List[QuestionItem])
def get_questions(
    category: Optional[str] = None,
    count: int = 10,
    difficulty: Optional[str] = None,
):
    questions = practice_service.get_random_questions(category, count, difficulty)
    return questions


@router.get("/questions/{question_id}", response_model=QuestionItem)
def get_question(question_id: str):
    question = practice_service.get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return question


@router.post("/check", response_model=PracticeCheckResponse)
async def check_answer(request: PracticeCheckRequest):
    result = await practice_service.check_answer(
        request.question.model_dump(), request.user_answer
    )
    return result


@router.post("/record")
def save_question_record(
    question_id: str,
    category: str = "",
    is_correct: int = 0,
    answer_text: str = "",
    is_collected: int = 0,
    quality_score: int = 60,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(QuestionRecord)
        .filter(QuestionRecord.question_id == question_id)
        .first()
    )

    if existing:
        existing.category = category or existing.category
        existing.is_correct = is_correct
        existing.answer_text = answer_text
        existing.is_collected = is_collected
        existing.review_count = (existing.review_count or 0) + 1
        existing.last_review_at = datetime.now()
        next_review_str = practice_service.calculate_next_review(
            quality_score, existing.review_count
        )
        existing.next_review_at = datetime.fromisoformat(next_review_str)
    else:
        next_review_str = practice_service.calculate_next_review(quality_score, 1)
        record = QuestionRecord(
            question_id=question_id,
            category=category,
            is_correct=is_correct,
            answer_text=answer_text,
            is_collected=is_collected,
            review_count=1,
            last_review_at=datetime.now(),
            next_review_at=datetime.fromisoformat(next_review_str),
        )
        db.add(record)

    db.commit()
    return {"status": "success"}


@router.get("/collected", response_model=List[QuestionRecordResponse])
def get_collected_questions(db: Session = Depends(get_db)):
    records = (
        db.query(QuestionRecord)
        .filter(QuestionRecord.is_collected == 1)
        .order_by(QuestionRecord.updated_at.desc())
        .all()
    )
    return records


@router.get("/review", response_model=List[QuestionRecordResponse])
def get_review_questions(db: Session = Depends(get_db)):
    records = (
        db.query(QuestionRecord)
        .filter(QuestionRecord.next_review_at <= datetime.now())
        .order_by(QuestionRecord.next_review_at.asc())
        .limit(20)
        .all()
    )
    return records


@router.post("/collect/{question_id}")
def toggle_collect(
    question_id: str,
    collected: bool = True,
    db: Session = Depends(get_db),
):
    record = (
        db.query(QuestionRecord)
        .filter(QuestionRecord.question_id == question_id)
        .first()
    )
    if not record:
        record = QuestionRecord(question_id=question_id, is_collected=1 if collected else 0)
        db.add(record)
    else:
        record.is_collected = 1 if collected else 0
    db.commit()
    return {"status": "success", "collected": collected}


@router.get("/stats")
def get_practice_stats(db: Session = Depends(get_db)):
    return practice_service.get_stats(db)
