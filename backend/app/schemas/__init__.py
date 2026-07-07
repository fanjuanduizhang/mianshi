from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class UserProfileBase(BaseModel):
    username: str = "default_user"
    education: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    target_position: Optional[str] = None
    skills: List[str] = Field(default_factory=list)


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileResponse(UserProfileBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JDAnalysisBase(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    raw_text: str


class JDAnalysisCreate(JDAnalysisBase):
    extracted_skills: List[dict] = Field(default_factory=list)
    match_score: Optional[float] = None
    gap_analysis: dict = Field(default_factory=dict)
    ai_analysis: Optional[str] = None


class JDAnalysisResponse(BaseModel):
    id: int
    company: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    match_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class JDAnalysisDetailResponse(JDAnalysisResponse):
    raw_text: str
    extracted_skills: List[dict] = Field(default_factory=list)
    gap_analysis: dict = Field(default_factory=dict)
    ai_analysis: Optional[str] = None


class StudyPlanBase(BaseModel):
    jd_id: Optional[int] = None
    title: str
    plan: List[dict] = Field(default_factory=list)
    priority: int = 0
    status: str = "pending"
    estimated_hours: int = 0


class StudyPlanCreate(StudyPlanBase):
    pass


class StudyPlanResponse(StudyPlanBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuestionRecordBase(BaseModel):
    question_id: str
    category: Optional[str] = None
    is_correct: Optional[int] = None
    answer_text: Optional[str] = None
    is_collected: int = 0
    review_count: int = 0


class QuestionRecordCreate(QuestionRecordBase):
    next_review_at: Optional[datetime] = None
    last_review_at: Optional[datetime] = None


class QuestionRecordResponse(QuestionRecordBase):
    id: int
    next_review_at: Optional[datetime] = None
    last_review_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InterviewSessionBase(BaseModel):
    position: Optional[str] = None
    questions: List[dict] = Field(default_factory=list)
    answers: dict = Field(default_factory=dict)
    score: Optional[float] = None
    feedback: Optional[str] = None
    duration: Optional[int] = None


class InterviewSessionCreate(InterviewSessionBase):
    pass


class InterviewSessionResponse(BaseModel):
    id: int
    position: Optional[str] = None
    score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewSessionDetailResponse(InterviewSessionResponse):
    questions: List[dict] = Field(default_factory=list)
    answers: dict = Field(default_factory=dict)
    feedback: Optional[str] = None
    duration: Optional[int] = None


class ResumeAnalysisBase(BaseModel):
    file_name: Optional[str] = None
    resume_text: str
    target_position: Optional[str] = None


class ResumeAnalysisCreate(ResumeAnalysisBase):
    analysis: dict = Field(default_factory=dict)
    suggestions: Optional[str] = None
    skills: List[dict] = Field(default_factory=list)


class ResumeAnalysisResponse(BaseModel):
    id: int
    file_name: Optional[str] = None
    target_position: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeAnalysisDetailResponse(ResumeAnalysisResponse):
    resume_text: str
    analysis: dict = Field(default_factory=dict)
    suggestions: Optional[str] = None
    skills: List[dict] = Field(default_factory=list)


class DashboardStats(BaseModel):
    total_questions: int
    practiced: int
    mastered: int
    collected: int
    overall_progress: float
    category_stats: List[dict] = Field(default_factory=list)
    recent_interviews: List[dict] = Field(default_factory=list)
    jd_list: List[dict] = Field(default_factory=list)


class QuestionItem(BaseModel):
    id: str
    question: str
    answer: str
    category: str
    difficulty: str


class RAGQueryRequest(BaseModel):
    question: str
    top_k: int = 3


class RAGAnswerResponse(BaseModel):
    answer: str
    relevant_docs: List[dict] = Field(default_factory=list)


class PracticeCheckRequest(BaseModel):
    question: QuestionItem
    user_answer: str


class PracticeCheckResponse(BaseModel):
    score: int
    is_correct: bool
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    key_points_missed: List[str] = Field(default_factory=list)


class MockInterviewStartRequest(BaseModel):
    position: str = ""
    question_count: int = 5


class MockInterviewEvaluateRequest(BaseModel):
    question: dict
    user_answer: str
    question_index: int
    total_score: float = 0


class MockInterviewSummaryRequest(BaseModel):
    position: str
    answers: List[dict] = Field(default_factory=list)
    total_score: float
    question_count: int


class ResumeAnalyzeRequest(BaseModel):
    resume_text: str
    target_position: str = ""


class ResumeAnalyzeResponse(BaseModel):
    analysis: dict
    suggestions: str
    skills: List[dict] = Field(default_factory=list)


class JDInfo(BaseModel):
    company: Optional[str] = None
    position: str
    location: Optional[str] = None
    skills: List[dict] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)


class JDMatchRequest(BaseModel):
    jd_text: str
    user_skills: List[str] = Field(default_factory=list)
    resume_text: str = ""


class JDMatchResponse(BaseModel):
    match_score: float
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[dict] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    gap_summary: str


class StudyPlanGenerateRequest(BaseModel):
    gap_analysis: dict
    target_position: str = ""


class SkillExtractionRequest(BaseModel):
    resume_text: str


class SkillExtractionResponse(BaseModel):
    skills: List[dict] = Field(default_factory=list)
