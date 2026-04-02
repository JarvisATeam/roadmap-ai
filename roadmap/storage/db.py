"""Database helpers for roadmap."""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

DEFAULT_DB_PATH = Path.home() / ".roadmap" / "roadmap.db"


def _db_path() -> Path:
    override = os.environ.get("ROADMAP_DB_PATH")
    if override:
        return Path(override).expanduser()
    return DEFAULT_DB_PATH


def init_db():
    """Initialize database and create tables."""
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{path}")
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get a database session."""
    path = _db_path()
    engine = create_engine(f"sqlite:///{path}")
    Session = sessionmaker(bind=engine)
    return Session()
