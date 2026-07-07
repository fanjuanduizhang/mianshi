from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, default="default_user")
    education = Column(String, nullable=True)
    school = Column(String, nullable=True)
    major = Column(String, nullable=True)
    target_position = Column(String, nullable=True)
    skills_json = Column(Text, default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JobDescription(Base):
    __tablename__ = "job_description"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, nullable=True)
    position = Column(String, nullable=True)
    location = Column(String, nullable=True)
    raw_text = Column(Text, nullable=False)
    extracted_skills_json = Column(Text, nullable=True)
    match_score = Column(Float, nullable=True)
    gap_analysis_json = Column(Text, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    study_plans = relationship("StudyPlan", back_populates="jd", cascade="all, delete-orphan")


class StudyPlan(Base):
    __tablename__ = "study_plan"

    id = Column(Integer, primary_key=True, index=True)
    jd_id = Column(Integer, ForeignKey("job_description.id"), nullable=True)
    title = Column(String, nullable=False)
    plan_json = Column(Text, nullable=False)
    priority = Column(Integer, default=0)
    status = Column(String, default="pending")
    estimated_hours = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    jd = relationship("JobDescription", back_populates="study_plans")


class QuestionRecord(Base):
    __tablename__ = "question_record"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=True)
    is_correct = Column(Integer, nullable=True)
    answer_text = Column(Text, nullable=True)
    is_collected = Column(Integer, default=0)
    review_count = Column(Integer, default=0)
    next_review_at = Column(DateTime(timezone=True), nullable=True)
    last_review_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, nullable=False)
    mastered_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InterviewSession(Base):
    __tablename__ = "interview_session"

    id = Column(Integer, primary_key=True, index=True)
    position = Column(String, nullable=True)
    questions_json = Column(Text, nullable=True)
    answers_json = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=True)
    resume_text = Column(Text, nullable=True)
    target_position = Column(String, nullable=True)
    analysis_json = Column(Text, nullable=True)
    suggestions = Column(Text, nullable=True)
    skills_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
