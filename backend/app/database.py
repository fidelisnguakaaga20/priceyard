from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


@lru_cache
def get_engine() -> Engine:
    """Create the PostgreSQL engine lazily so non-database endpoints can still start."""
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required for database operations")

    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=3,
        max_overflow=2,
        pool_recycle=300,
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        expire_on_commit=False,
    )


def get_db() -> Generator[Session, None, None]:
    """FastAPI database-session dependency for later API stages."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


def verify_database_connection() -> None:
    """Fail fast if PostgreSQL cannot be reached."""
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
