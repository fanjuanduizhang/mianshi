from app.services.rag_service import RAGService
from app.services.resume_service import ResumeService
from app.services.practice_service import PracticeService
from app.services.interview_service import MockInterviewService
from app.services.jd_service import JDService

rag_service = RAGService()
resume_service = ResumeService()
practice_service = PracticeService()
interview_service = MockInterviewService()
jd_service = JDService()

__all__ = [
    "rag_service",
    "resume_service",
    "practice_service",
    "interview_service",
    "jd_service",
]
