from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import practice_service, rag_service
from app.models import InterviewSession, JobDescription
from app.schemas import DashboardStats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    stats = practice_service.get_stats(db)

    recent_interviews = (
        db.query(InterviewSession)
        .order_by(InterviewSession.created_at.desc())
        .limit(5)
        .all()
    )

    jd_list = (
        db.query(JobDescription)
        .order_by(JobDescription.created_at.desc())
        .limit(5)
        .all()
    )

    stats["recent_interviews"] = [
        {
            "id": iv.id,
            "position": iv.position,
            "score": iv.score,
            "created_at": iv.created_at.isoformat() if iv.created_at else None,
        }
        for iv in recent_interviews
    ]

    stats["jd_list"] = [
        {
            "id": jd.id,
            "company": jd.company,
            "position": jd.position,
            "match_score": jd.match_score,
            "created_at": jd.created_at.isoformat() if jd.created_at else None,
        }
        for jd in jd_list
    ]

    return stats
