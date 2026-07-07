from fastapi import APIRouter
from app.services import resume_service
from app.schemas import SkillExtractionRequest, SkillExtractionResponse

router = APIRouter()


@router.post("/extract", response_model=SkillExtractionResponse)
async def extract_skills(request: SkillExtractionRequest):
    skills = await resume_service.extract_skills(request.resume_text)
    return {"skills": skills}


@router.post("/wordcloud")
def generate_wordcloud(request: dict):
    skills = request.get("skills", [])
    image_data = resume_service.generate_wordcloud(skills)
    return {"image": image_data}
