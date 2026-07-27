"""
CareerCompass AI — Database connection layer.

Phase 6:
  - SQLite engine + session setup via SQLAlchemy
  - Tables: users, chat_history (see models.py)
  - get_db() dependency for FastAPI routes
  - init_db() creates tables on startup if they don't exist yet
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database/career.db")

# check_same_thread=False is required for SQLite when used with FastAPI's
# threaded request handling (each request may run on a different thread).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session and always closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables that don't exist yet. Safe to call on every startup."""
    # Import models here (not at module top) to avoid circular imports between
    # database.py and models.py, since models.py imports Base from this module.
    from backend import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
