from fastapi import APIRouter
from app.api.v1 import (
    dashboard,
    practice,
    interview,
    resume,
    jd,
    rag,
    skills,
    user,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(dashboard.router, prefix="/dashboard", tags=["仪表盘"])
api_router.include_router(practice.router, prefix="/practice", tags=["刷题练习"])
api_router.include_router(interview.router, prefix="/interview", tags=["模拟面试"])
api_router.include_router(resume.router, prefix="/resume", tags=["简历优化"])
api_router.include_router(jd.router, prefix="/jd", tags=["JD匹配"])
api_router.include_router(rag.router, prefix="/rag", tags=["智能问答"])
api_router.include_router(skills.router, prefix="/skills", tags=["技能分析"])
api_router.include_router(user.router, prefix="/user", tags=["用户"])
