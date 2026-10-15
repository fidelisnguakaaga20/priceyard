from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import Request

from app.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


@lru_cache
def get_engine() -> Engine:
    """Create the PostgreSQL engine lazily so non-database endpoints can still start."""
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required for database operations")

    if settings.app_env == "test":
        if settings.database_url != "sqlite+pysqlite:///:memory:":
            raise RuntimeError("Test database must be an isolated in-memory database")
        return create_engine(settings.database_url, poolclass=StaticPool, connect_args={"check_same_thread": False})
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


class AtomicSession(Session):
    """Only the HTTP unit of work may commit; service commits become flushes."""

    def commit(self) -> None:
        self.flush()


def get_db(request: Request) -> Session:
    """Share one unit of work, finalized before its HTTP response is returned."""
    if not hasattr(request.state, "database_session"):
        request.state.database_session = AtomicSession(bind=get_engine(), autoflush=False, expire_on_commit=False)
    return request.state.database_session


def verify_database_connection() -> None:
    """Fail fast if PostgreSQL cannot be reached."""
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
