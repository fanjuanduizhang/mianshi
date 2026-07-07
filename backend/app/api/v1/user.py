from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserProfile
from app.schemas import UserProfileUpdate, UserProfileResponse
import json

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
def get_user_profile(db: Session = Depends(get_db)):
    profile = (
        db.query(UserProfile).filter(UserProfile.username == "default_user").first()
    )
    if not profile:
        profile = UserProfile(username="default_user")
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return {
        "id": profile.id,
        "username": profile.username,
        "education": profile.education,
        "school": profile.school,
        "major": profile.major,
        "target_position": profile.target_position,
        "skills": json.loads(profile.skills_json or "[]"),
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }


@router.put("/profile", response_model=UserProfileResponse)
def update_user_profile(
    data: UserProfileUpdate,
    db: Session = Depends(get_db),
):
    profile = (
        db.query(UserProfile).filter(UserProfile.username == "default_user").first()
    )
    if not profile:
        profile = UserProfile(username="default_user")
        db.add(profile)

    profile.education = data.education
    profile.school = data.school
    profile.major = data.major
    profile.target_position = data.target_position
    profile.skills_json = json.dumps(data.skills, ensure_ascii=False)

    db.commit()
    db.refresh(profile)

    return {
        "id": profile.id,
        "username": profile.username,
        "education": profile.education,
        "school": profile.school,
        "major": profile.major,
        "target_position": profile.target_position,
        "skills": json.loads(profile.skills_json or "[]"),
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }
