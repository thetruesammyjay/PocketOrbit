from collections.abc import Generator
from functools import lru_cache

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not configured.")
    database_url = settings.database_url
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_timeout=10,
        pool_size=5,
        max_overflow=10,
    )
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    try:
        session_factory = get_session_factory()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Database access is not configured.") from exc

    with session_factory() as session:
        yield session


def get_optional_db() -> Generator[Session | None, None, None]:
    """Provide a database session when configured, otherwise support local demo mode."""
    if not settings.database_url:
        yield None
        return
    try:
        session_factory = get_session_factory()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Database access is not configured.") from exc

    with session_factory() as session:
        yield session
