"""
CareerCompass AI — FastAPI entrypoint.

Phase 4/5/6 scope: real endpoints for profile management, AI-powered career
guidance chat, resume review, roadmap generation, skill-gap analysis, and
chat history — all wired to ai.py (Google Gemini) and database.py/models.py (SQLite).

Scope note: the current frontend has no login flow, so this app is
single-profile. There is exactly one Profile row (id=1) that gets created on
first save and updated afterward. All chat history is attached to it.
"""

from typing import List

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# In Docker, docker-compose's env_file already injects these vars, so this is a
# no-op there. It matters when running `uvicorn` directly on a host machine.
load_dotenv()

from backend import ai
from backend.database import get_db, init_db
from backend.models import (
    ChatHistory,
    ChatRequest,
    ChatResponse,
    HistoryItemOut,
    Profile,
    ProfileIn,
    ProfileOut,
    ResumeReviewRequest,
    ResumeReviewResponse,
    RoadmapRequest,
    RoadmapResponse,
    SkillGapRequest,
    SkillGapResponse,
)

app = FastAPI(
    title="CareerCompass AI",
    description="AI Career Mentor for Engineering Students",
    version="0.4.0",
)
# Serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("frontend/index.html")

@app.get("/pages/dashboard.html")
def dashboard():
    return FileResponse("frontend/pages/dashboard.html")


@app.get("/pages/chat.html")
def chat():
    return FileResponse("frontend/pages/chat.html")


@app.get("/pages/about.html")
def about():
    return FileResponse("frontend/pages/about.html")


@app.get("/pages/history.html")
def history_page():
    return FileResponse("frontend/pages/history.html")


@app.get("/pages/resume.html")
def resume():
    return FileResponse("frontend/pages/resume.html")
# Allow the frontend (served separately) to call this API during development.
# Locked down further before deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    """Simple liveness check used to confirm Docker + FastAPI wiring works."""
    return {"status": "ok", "service": "career-compass-ai-backend"}


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

DEFAULT_PROFILE_ID = 1


def _get_or_create_profile(db: Session) -> Profile:
    profile = db.query(Profile).filter(Profile.id == DEFAULT_PROFILE_ID).first()
    if profile is None:
        profile = Profile(id=DEFAULT_PROFILE_ID)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@app.get("/profile", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db)
    return ProfileOut.from_orm_model(profile)


@app.post("/profile", response_model=ProfileOut)
def save_profile(payload: ProfileIn, db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db)
    profile.branch = payload.branch
    profile.semester = payload.semester
    profile.skills = payload.skills
    profile.interests = payload.interests
    profile.goal = payload.goal
    db.commit()
    db.refresh(profile)
    return ProfileOut.from_orm_model(profile)


def _profile_dict(profile: Profile) -> dict:
    return ProfileOut.from_orm_model(profile).dict()


# ---------------------------------------------------------------------------
# Career guidance chat
# ---------------------------------------------------------------------------


@app.post("/career-guidance", response_model=ChatResponse)
def career_guidance(payload: ChatRequest, db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db)
    answer = ai.get_career_guidance(_profile_dict(profile), payload.question)

    entry = ChatHistory(profile_id=profile.id, question=payload.question, answer=answer)
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return ChatResponse(question=entry.question, answer=entry.answer, created_at=entry.created_at)


@app.get("/history", response_model=List[HistoryItemOut])
def get_history(db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db)
    entries = (
        db.query(ChatHistory)
        .filter(ChatHistory.profile_id == profile.id)
        .order_by(ChatHistory.created_at.desc())
        .all()
    )
    return [
        HistoryItemOut(id=e.id, question=e.question, answer=e.answer, created_at=e.created_at)
        for e in entries
    ]


# ---------------------------------------------------------------------------
# Roadmap
# ---------------------------------------------------------------------------


@app.post("/roadmap", response_model=RoadmapResponse)
def roadmap(payload: RoadmapRequest, db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db)
    result = ai.generate_roadmap(_profile_dict(profile), payload.domain)
    result["domain"] = payload.domain  # trust our own request over whatever the model echoed back
    try:
        return RoadmapResponse(**result)
    except TypeError as exc:
        raise HTTPException(status_code=502, detail="AI returned an unexpected roadmap shape.") from exc


# ---------------------------------------------------------------------------
# Resume review
# ---------------------------------------------------------------------------


@app.post("/resume-review", response_model=ResumeReviewResponse)
def resume_review(payload: ResumeReviewRequest):
    result = ai.review_resume(payload.resume_text)
    try:
        return ResumeReviewResponse(**result)
    except TypeError as exc:
        raise HTTPException(status_code=502, detail="AI returned an unexpected resume review shape.") from exc


# ---------------------------------------------------------------------------
# Skill gap
# ---------------------------------------------------------------------------


@app.post("/skill-gap", response_model=SkillGapResponse)
def skill_gap(payload: SkillGapRequest, db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db)
    result = ai.analyze_skill_gap(_profile_dict(profile), payload.target_role)
    result["target_role"] = payload.target_role  # trust our own request over whatever the model echoed back
    try:
        return SkillGapResponse(**result)
    except TypeError as exc:
        raise HTTPException(status_code=502, detail="AI returned an unexpected skill-gap shape.") from exc
