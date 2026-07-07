from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services import jd_service
from app.models import JobDescription, StudyPlan
from app.schemas import (
    JDMatchRequest,
    JDMatchResponse,
    StudyPlanGenerateRequest,
    JDAnalysisResponse,
    JDAnalysisDetailResponse,
    StudyPlanResponse,
)
import json

router = APIRouter()


@router.post("/extract")
async def extract_jd_info(request: dict):
    jd_text = request.get("jd_text", "")
    result = await jd_service.extract_jd_info(jd_text)
    return result


@router.post("/match", response_model=JDMatchResponse)
async def analyze_match(request: JDMatchRequest):
    result = await jd_service.analyze_match(
        request.jd_text, request.user_skills, request.resume_text
    )
    return result


@router.post("/save")
async def save_jd_analysis(
    request: dict,
    db: Session = Depends(get_db),
):
    jd = JobDescription(
        company=request.get("company"),
        position=request.get("position"),
        location=request.get("location"),
        raw_text=request.get("raw_text"),
        extracted_skills_json=json.dumps(
            request.get("extracted_skills", []), ensure_ascii=False
        ),
        match_score=request.get("match_score"),
        gap_analysis_json=json.dumps(
            request.get("gap_analysis", {}), ensure_ascii=False
        ),
        ai_analysis=request.get("ai_analysis"),
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)
    return {"id": jd.id}


@router.get("/list", response_model=List[JDAnalysisResponse])
def get_jd_list(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    jd_list = (
        db.query(JobDescription)
        .order_by(JobDescription.created_at.desc())
        .limit(limit)
        .all()
    )
    return jd_list


@router.get("/{jd_id}", response_model=JDAnalysisDetailResponse)
def get_jd_detail(
    jd_id: int,
    db: Session = Depends(get_db),
):
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="JD不存在")
    return {
        "id": jd.id,
        "company": jd.company,
        "position": jd.position,
        "location": jd.location,
        "match_score": jd.match_score,
        "created_at": jd.created_at,
        "raw_text": jd.raw_text,
        "extracted_skills": json.loads(jd.extracted_skills_json or "[]"),
        "gap_analysis": json.loads(jd.gap_analysis_json or "{}"),
        "ai_analysis": jd.ai_analysis,
    }


@router.post("/study-plan/generate")
async def generate_study_plan(request: StudyPlanGenerateRequest):
    weeks = await jd_service.generate_study_plan(
        request.gap_analysis, request.target_position
    )
    return {"weeks": weeks}


@router.post("/study-plan/save")
async def save_study_plan(
    request: dict,
    db: Session = Depends(get_db),
):
    plan = StudyPlan(
        jd_id=request.get("jd_id"),
        title=request.get("title"),
        plan_json=json.dumps(request.get("plan", []), ensure_ascii=False),
        priority=request.get("priority", 0),
        status=request.get("status", "pending"),
        estimated_hours=request.get("estimated_hours", 0),
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return {"id": plan.id}


@router.get("/study-plan/list", response_model=List[StudyPlanResponse])
def get_study_plans(
    status: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(StudyPlan)
    if status:
        query = query.filter(StudyPlan.status == status)
    plans = query.order_by(StudyPlan.priority.desc(), StudyPlan.created_at.desc()).all()

    result = []
    for p in plans:
        result.append(
            {
                "id": p.id,
                "jd_id": p.jd_id,
                "title": p.title,
                "plan": json.loads(p.plan_json or "[]"),
                "priority": p.priority,
                "status": p.status,
                "estimated_hours": p.estimated_hours,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
            }
        )
    return result


@router.put("/study-plan/{plan_id}/status")
def update_study_plan_status(
    plan_id: int,
    status: str,
    db: Session = Depends(get_db),
):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id).first()
    if not plan:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="学习计划不存在")
    plan.status = status
    db.commit()
    return {"status": "success"}
