"""
CareerCompass AI — Data models.

Phase 6:
  - SQLAlchemy ORM models: Profile, ChatHistory
  - Pydantic request/response schemas for the API endpoints

Note on scope: the current frontend has no login/auth flow (see dashboard.html),
so this phase treats the app as single-profile — there is one Profile row that
gets created/updated, and all chat history hangs off it. Multi-user auth can be
layered in later without changing these endpoint contracts much.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.database import Base

# ---------------------------------------------------------------------------
# SQLAlchemy ORM models
# ---------------------------------------------------------------------------


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    branch = Column(String, nullable=True)
    semester = Column(String, nullable=True)
    skills = Column(String, nullable=True)      # comma-separated, e.g. "Python, C, HTML"
    interests = Column(String, nullable=True)   # comma-separated
    goal = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chat_history = relationship("ChatHistory", back_populates="profile", cascade="all, delete-orphan")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("Profile", back_populates="chat_history")


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


def _split_csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


class ProfileIn(BaseModel):
    branch: Optional[str] = None
    semester: Optional[str] = None
    skills: Optional[str] = Field(default=None, description="Comma-separated list, e.g. 'Python, C, HTML/CSS'")
    interests: Optional[str] = Field(default=None, description="Comma-separated list, e.g. 'AI, Cloud'")
    goal: Optional[str] = None


class ProfileOut(BaseModel):
    id: int
    branch: Optional[str] = None
    semester: Optional[str] = None
    skills: List[str] = []
    interests: List[str] = []
    goal: Optional[str] = None

    @classmethod
    def from_orm_model(cls, profile: "Profile") -> "ProfileOut":
        return cls(
            id=profile.id,
            branch=profile.branch,
            semester=profile.semester,
            skills=_split_csv(profile.skills),
            interests=_split_csv(profile.interests),
            goal=profile.goal,
        )


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    question: str
    answer: str
    created_at: datetime


class HistoryItemOut(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime


class ResumeReviewRequest(BaseModel):
    resume_text: str = Field(..., min_length=20, description="Raw resume text pasted by the student")


class ResumeReviewResponse(BaseModel):
    strengths: List[str]
    improvements: List[str]
    summary: str


class RoadmapRequest(BaseModel):
    domain: str = Field(..., description="e.g. 'AI/ML', 'VLSI', 'Cybersecurity'")


class RoadmapStage(BaseModel):
    title: str
    duration: str
    topics: List[str]
    resources: List[str]


class RoadmapResponse(BaseModel):
    domain: str
    stages: List[RoadmapStage]


class SkillGapRequest(BaseModel):
    target_role: str = Field(..., description="e.g. 'Data Scientist', 'Embedded Systems Engineer'")


class SkillGapResponse(BaseModel):
    target_role: str
    known_skills: List[str]
    missing_skills: List[str]
    recommended_resources: List[str]
