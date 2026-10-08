from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "environment": settings.app_env,
        "databaseConfigured": bool(settings.database_url),
    }


@router.get("/ready")
def readiness(session: Session = Depends(get_db)) -> dict[str, str]:
    """Check database connectivity and confirm the installed schema is current."""
    try:
        session.execute(text("SELECT 1"))
        current_revision = session.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one_or_none()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The database schema is not ready.",
        ) from exc

    migration_config = Config()
    migration_config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[3] / "migrations")
    )
    try:
        migration_head = ScriptDirectory.from_config(migration_config).get_current_head()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The application migration metadata is unavailable.",
        ) from exc

    if current_revision != migration_head:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The database schema is behind the current application revision.",
        )
    return {"status": "ready", "database": "connected", "schema": "current"}
