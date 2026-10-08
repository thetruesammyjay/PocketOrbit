from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Integer, String, cast, func, literal, select, text, union_all
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.activity import Transaction
from app.models.asset import Asset
from app.models.audit_event import AuditEvent
from app.models.import_job import ImportJob
from app.models.portfolio import Portfolio
from app.models.source import Source
from app.models.sync_job import SyncJob
from app.models.user import User
from app.services.wallet_service import wallet_capabilities

router = APIRouter()
PAGE_SIZE_MAX = 100


def require_admin(
    session: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> User:
    allowed_emails = {
        item.strip().lower() for item in settings.admin_emails.split(",") if item.strip()
    }
    if not allowed_emails or user.email.strip().lower() not in allowed_emails:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return user


def _record_admin_view(session: Session, admin: User, page: str) -> None:
    session.add(
        AuditEvent(
            actor_id=admin.id,
            action=f"admin.{page}.view",
            target_type="admin_page",
            target_id=page,
        )
    )
    session.commit()


def _mask_address(address: str | None) -> str | None:
    if not address:
        return None
    if len(address) <= 12:
        return f"{address[:3]}…{address[-3:]}"
    return f"{address[:6]}…{address[-4:]}"


@router.get("/status")
def admin_status(
    session: Session = Depends(get_db), admin: User = Depends(require_admin)
) -> dict[str, object]:
    _record_admin_view(session, admin, "status")
    return {"configured": True, "message": "Administrator access is configured."}


@router.get("/overview")
def admin_overview(
    session: Session = Depends(get_db), admin: User = Depends(require_admin)
) -> dict[str, object]:
    _record_admin_view(session, admin, "overview")
    counts = {
        "users": session.scalar(select(func.count()).select_from(User)) or 0,
        "portfolios": session.scalar(select(func.count()).select_from(Portfolio)) or 0,
        "sources": session.scalar(select(func.count()).select_from(Source)) or 0,
        "imports": session.scalar(select(func.count()).select_from(ImportJob)) or 0,
        "assets": session.scalar(select(func.count()).select_from(Asset)) or 0,
        "transactions": session.scalar(select(func.count()).select_from(Transaction)) or 0,
        "failedSyncs": session.scalar(
            select(func.count()).select_from(SyncJob).where(SyncJob.status == "failed")
        )
        or 0,
    }
    recent_events = _audit_rows(session, limit=10)
    return {"counts": counts, "recentEvents": recent_events}


@router.get("/users")
def admin_users(
    offset: int = Query(default=0, ge=0, le=50_000),
    limit: int = Query(default=50, ge=1, le=PAGE_SIZE_MAX),
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict[str, object]:
    _record_admin_view(session, admin, "users")
    portfolio_counts = (
        select(Portfolio.user_id, func.count(Portfolio.id).label("portfolio_count"))
        .group_by(Portfolio.user_id)
        .subquery()
    )
    rows = session.execute(
        select(User, func.coalesce(portfolio_counts.c.portfolio_count, 0))
        .outerjoin(portfolio_counts, portfolio_counts.c.user_id == User.id)
        .order_by(User.created_at.desc(), User.id)
        .offset(offset)
        .limit(limit)
    ).all()
    total = session.scalar(select(func.count()).select_from(User)) or 0
    return {
        "total": total,
        "items": [
            {
                "id": str(user.id),
                "email": user.email,
                "emailVerified": user.email_verified_at is not None,
                "createdAt": user.created_at,
                "portfolioCount": portfolio_count,
            }
            for user, portfolio_count in rows
        ],
    }


@router.get("/portfolios")
def admin_portfolios(
    offset: int = Query(default=0, ge=0, le=50_000),
    limit: int = Query(default=50, ge=1, le=PAGE_SIZE_MAX),
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict[str, object]:
    _record_admin_view(session, admin, "portfolios")
    rows = session.execute(
        select(Portfolio, User.email)
        .outerjoin(User, User.id == Portfolio.user_id)
        .order_by(Portfolio.created_at.desc(), Portfolio.id)
        .offset(offset)
        .limit(limit)
    ).all()
    total = session.scalar(select(func.count()).select_from(Portfolio)) or 0
    return {
        "total": total,
        "items": [
            {
                "id": str(portfolio.id),
                "name": portfolio.name,
                "ownerEmail": owner_email,
                "currency": portfolio.reporting_currency,
                "createdAt": portfolio.created_at,
            }
            for portfolio, owner_email in rows
        ],
    }


@router.get("/imports")
def admin_imports(
    offset: int = Query(default=0, ge=0, le=50_000),
    limit: int = Query(default=50, ge=1, le=PAGE_SIZE_MAX),
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict[str, object]:
    _record_admin_view(session, admin, "imports")
    rows = session.execute(
        select(ImportJob, Portfolio.name, User.email)
        .join(Portfolio, Portfolio.id == ImportJob.portfolio_id)
        .outerjoin(User, User.id == Portfolio.user_id)
        .order_by(ImportJob.created_at.desc(), ImportJob.id)
        .offset(offset)
        .limit(limit)
    ).all()
    total = session.scalar(select(func.count()).select_from(ImportJob)) or 0
    return {
        "total": total,
        "items": [
            {
                "id": str(job.id),
                "filename": job.filename,
                "status": job.status,
                "rowsReceived": job.rows_received,
                "rowsAccepted": job.rows_accepted,
                "rowsRejected": job.rows_rejected,
                "portfolio": portfolio_name,
                "ownerEmail": owner_email,
                "createdAt": job.created_at,
            }
            for job, portfolio_name, owner_email in rows
        ],
    }


@router.get("/sources")
def admin_sources(
    offset: int = Query(default=0, ge=0, le=50_000),
    limit: int = Query(default=50, ge=1, le=PAGE_SIZE_MAX),
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict[str, object]:
    _record_admin_view(session, admin, "sources")
    rows = session.execute(
        select(Source, Portfolio.name, User.email)
        .join(Portfolio, Portfolio.id == Source.portfolio_id)
        .outerjoin(User, User.id == Portfolio.user_id)
        .order_by(Source.created_at.desc(), Source.id)
        .offset(offset)
        .limit(limit)
    ).all()
    total = session.scalar(select(func.count()).select_from(Source)) or 0
    return {
        "total": total,
        "items": [
            {
                "id": str(source.id),
                "name": source.name,
                "kind": source.kind,
                "network": source.network_id,
                "address": _mask_address(source.public_address),
                "quality": source.quality_status,
                "portfolio": portfolio_name,
                "ownerEmail": owner_email,
                "lastUpdatedAt": source.retrieved_at,
                "createdAt": source.created_at,
            }
            for source, portfolio_name, owner_email in rows
        ],
    }


@router.get("/assets")
def admin_assets(
    offset: int = Query(default=0, ge=0, le=50_000),
    limit: int = Query(default=50, ge=1, le=PAGE_SIZE_MAX),
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict[str, object]:
    _record_admin_view(session, admin, "assets")
    assets = session.scalars(
        select(Asset)
        .order_by(Asset.network_id, Asset.symbol, Asset.canonical_id)
        .offset(offset)
        .limit(limit)
    ).all()
    total = session.scalar(select(func.count()).select_from(Asset)) or 0
    return {
        "total": total,
        "items": [
            {
                "id": str(asset.id),
                "canonicalId": asset.canonical_id,
                "symbol": asset.symbol,
                "name": asset.name,
                "network": asset.network_id,
                "contract": _mask_address(asset.contract_address),
                "decimals": asset.decimals,
            }
            for asset in assets
        ],
    }


@router.get("/jobs")
def admin_jobs(
    offset: int = Query(default=0, ge=0, le=50_000),
    limit: int = Query(default=50, ge=1, le=PAGE_SIZE_MAX),
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict[str, object]:
    _record_admin_view(session, admin, "jobs")
    sync_statement = (
        select(
            SyncJob.id.label("id"),
            literal("wallet_sync").label("job_type"),
            SyncJob.status.label("status"),
            SyncJob.message.label("message"),
            Source.name.label("source"),
            Source.network_id.label("network"),
            Portfolio.name.label("portfolio"),
            User.email.label("owner_email"),
            SyncJob.created_at.label("created_at"),
            cast(literal(None), Integer).label("rows_accepted"),
            cast(literal(None), Integer).label("rows_rejected"),
        )
        .select_from(SyncJob)
        .join(Source, Source.id == SyncJob.source_id)
        .join(Portfolio, Portfolio.id == Source.portfolio_id)
        .outerjoin(User, User.id == Portfolio.user_id)
    )
    import_statement = (
        select(
            ImportJob.id.label("id"),
            literal("csv_import").label("job_type"),
            ImportJob.status.label("status"),
            cast(literal(None), String).label("message"),
            ImportJob.filename.label("source"),
            cast(literal(None), String).label("network"),
            Portfolio.name.label("portfolio"),
            User.email.label("owner_email"),
            ImportJob.created_at.label("created_at"),
            ImportJob.rows_accepted.label("rows_accepted"),
            ImportJob.rows_rejected.label("rows_rejected"),
        )
        .select_from(ImportJob)
        .join(Portfolio, Portfolio.id == ImportJob.portfolio_id)
        .outerjoin(User, User.id == Portfolio.user_id)
    )
    all_jobs = union_all(sync_statement, import_statement).subquery("admin_jobs")
    job_rows = session.execute(
        select(all_jobs)
        .order_by(all_jobs.c.created_at.desc(), all_jobs.c.id.desc())
        .offset(offset)
        .limit(limit)
    ).mappings()
    jobs = []
    for row in job_rows:
        message = row["message"]
        if row["job_type"] == "csv_import":
            message = f"{row['rows_accepted']} accepted / {row['rows_rejected']} rejected"
        jobs.append(
            {
                "id": str(row["id"]),
                "jobType": row["job_type"],
                "status": row["status"],
                "message": message,
                "source": row["source"],
                "network": row["network"],
                "portfolio": row["portfolio"],
                "ownerEmail": row["owner_email"],
                "createdAt": row["created_at"],
            }
        )
    total = (session.scalar(select(func.count()).select_from(SyncJob)) or 0) + (
        session.scalar(select(func.count()).select_from(ImportJob)) or 0
    )
    return {"total": total, "items": jobs}


@router.get("/system")
def admin_system(
    session: Session = Depends(get_db), admin: User = Depends(require_admin)
) -> dict[str, object]:
    _record_admin_view(session, admin, "system")
    schema_revision = "unavailable"
    try:
        session.execute(text("SELECT 1"))
        revision = session.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one_or_none()
        schema_revision = str(revision) if revision else "not_migrated"
    except SQLAlchemyError:
        session.rollback()

    expected_revision = "unknown"
    try:
        migration_config = Config()
        migration_config.set_main_option(
            "script_location", str(Path(__file__).resolve().parents[3] / "migrations")
        )
        expected_revision = (
            ScriptDirectory.from_config(migration_config).get_current_head() or "unknown"
        )
    except (OSError, RuntimeError, ValueError):
        expected_revision = "unavailable"

    return {
        "checks": [
            {
                "name": "Database",
                "status": (
                    "ready"
                    if schema_revision not in {"unavailable", "not_migrated"}
                    else "needs_attention"
                ),
                "details": "Database connection and migration revision check.",
            },
            {
                "name": "Schema revision",
                "status": "ready" if schema_revision == expected_revision else "needs_attention",
                "details": f"Installed: {schema_revision}; application head: {expected_revision}.",
            },
            {
                "name": "Email delivery",
                "status": (
                    "ready"
                    if settings.smtp_host and settings.smtp_from_email
                    else "not_configured"
                ),
                "details": "Account verification and recovery email configuration.",
            },
            {
                "name": "Pricing provider",
                "status": "ready" if settings.coingecko_api_key else "not_configured",
                "details": (
                    "CoinGecko API key presence only; provider reachability is not checked here."
                ),
            },
        ],
        "environment": settings.app_env,
        "walletCapabilities": wallet_capabilities(),
    }


@router.get("/settings")
def admin_settings(
    session: Session = Depends(get_db), admin: User = Depends(require_admin)
) -> dict[str, object]:
    _record_admin_view(session, admin, "settings")
    capabilities = wallet_capabilities()
    network_rows = [
        {
            "name": f"Wallet network: {network.get('name', 'unknown')}",
            "value": network.get("coverage", "unknown"),
            "configured": network.get("configured", False),
        }
        for network in capabilities.get("networks", [])
        if isinstance(network, dict)
    ]
    settings_rows = [
        {
            "name": "Database persistence",
            "value": "Enabled" if capabilities["persistence"] else "Disabled",
            "configured": capabilities["persistence"],
        },
        {
            "name": "Admin allowlist",
            "value": (
                f"{len([part for part in settings.admin_emails.split(',') if part.strip()])} "
                "account(s)"
            ),
            "configured": bool(settings.admin_emails.strip()),
        },
        {
            "name": "Email delivery",
            "value": "Configured"
            if settings.smtp_host and settings.smtp_from_email
            else "Not configured",
            "configured": bool(settings.smtp_host and settings.smtp_from_email),
        },
        {
            "name": "Price provider",
            "value": "CoinGecko" if settings.coingecko_api_key else "Not configured",
            "configured": bool(settings.coingecko_api_key),
        },
        *network_rows,
    ]
    return {"items": settings_rows}


@router.get("/audit")
def admin_audit(
    offset: int = Query(default=0, ge=0, le=50_000),
    limit: int = Query(default=50, ge=1, le=PAGE_SIZE_MAX),
    session: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict[str, object]:
    _record_admin_view(session, admin, "audit")
    return {
        "total": session.scalar(select(func.count()).select_from(AuditEvent)) or 0,
        "items": _audit_rows(session, offset=offset, limit=limit),
    }


def _audit_rows(session: Session, *, limit: int, offset: int = 0) -> list[dict[str, object]]:
    rows = session.execute(
        select(AuditEvent, User.email)
        .outerjoin(User, User.id == AuditEvent.actor_id)
        .order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return [
        {
            "id": str(event.id),
            "actorId": str(event.actor_id) if event.actor_id else None,
            "actorEmail": email,
            "action": event.action,
            "targetType": event.target_type,
            "targetId": event.target_id,
            "createdAt": event.created_at,
        }
        for event, email in rows
    ]
