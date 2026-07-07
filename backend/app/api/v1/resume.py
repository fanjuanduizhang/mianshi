from fastapi import APIRouter, UploadFile, File, Depends, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services import resume_service
from app.models import ResumeAnalysis
from app.schemas import (
    ResumeAnalyzeRequest,
    ResumeAnalyzeResponse,
    ResumeAnalysisResponse,
    ResumeAnalysisDetailResponse,
)
import json

router = APIRouter()


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    text = resume_service.extract_text_from_pdf(content)
    return {"filename": file.filename, "text": text}


@router.post("/analyze", response_model=ResumeAnalyzeResponse)
async def analyze_resume(request: ResumeAnalyzeRequest):
    analysis = await resume_service.analyze_resume(
        request.resume_text, request.target_position
    )
    suggestions = await resume_service.optimize_resume(
        request.resume_text, request.target_position
    )
    skills = await resume_service.extract_skills(request.resume_text)
    return {"analysis": analysis, "suggestions": suggestions, "skills": skills}


@router.post("/save")
async def save_resume_analysis(
    request: dict,
    db: Session = Depends(get_db),
):
    record = ResumeAnalysis(
        file_name=request.get("file_name"),
        resume_text=request.get("resume_text"),
        target_position=request.get("target_position"),
        analysis_json=json.dumps(request.get("analysis", {}), ensure_ascii=False),
        suggestions=request.get("suggestions"),
        skills_json=json.dumps(request.get("skills", []), ensure_ascii=False),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id}


@router.get("/records", response_model=List[ResumeAnalysisResponse])
def get_resume_records(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    records = (
        db.query(ResumeAnalysis)
        .order_by(ResumeAnalysis.created_at.desc())
        .limit(limit)
        .all()
    )
    return records


@router.get("/records/{record_id}", response_model=ResumeAnalysisDetailResponse)
def get_resume_detail(
    record_id: int,
    db: Session = Depends(get_db),
):
    record = db.query(ResumeAnalysis).filter(ResumeAnalysis.id == record_id).first()
    if not record:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="记录不存在")
    return {
        "id": record.id,
        "file_name": record.file_name,
        "target_position": record.target_position,
        "created_at": record.created_at,
        "resume_text": record.resume_text,
        "analysis": json.loads(record.analysis_json or "{}"),
        "suggestions": record.suggestions,
        "skills": json.loads(record.skills_json or "[]"),
    }


@router.post("/wordcloud")
def generate_wordcloud(request: dict):
    skills = request.get("skills", [])
    image_data = resume_service.generate_wordcloud(skills)
    return {"image": image_data}
