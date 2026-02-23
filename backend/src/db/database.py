"""SQLite database engine and session factory."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

_db_path = os.environ.get("DATABASE_URL", "sqlite:///./data/meme_generator.db")

database_engine = create_engine(
    _db_path,
    connect_args={"check_same_thread": False},
)

SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=database_engine,
)


def get_db() -> Session:
    """Dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_data_dir() -> None:
    """Create the data directories if they don't exist."""
    Path("data/templates").mkdir(parents=True, exist_ok=True)
