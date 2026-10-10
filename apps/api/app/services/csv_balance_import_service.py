import hashlib
from datetime import UTC, datetime
from pathlib import PurePosixPath
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.connectors.exchanges.csv.normalizer import parse_csv_balances
from app.models.balance import Balance
from app.models.import_job import ImportJob
from app.models.portfolio import Portfolio
from app.models.source import Source
from app.models.wallet_snapshot import WalletSnapshot
from app.schemas.common import QualityStatus
from app.schemas.imports import CsvBalanceFieldMapping, ImportResultRead
from app.services.csv_import_service import _resolve_or_create_asset
from app.services.persistent_portfolios import record_valuation_snapshot


def import_csv_balance_statement(
    session: Session,
    portfolio: Portfolio,
    filename: str,
    contents: bytes,
    mapping: CsvBalanceFieldMapping,
    *,
    source_id: UUID | None = None,
    source_name: str | None = None,
) -> ImportResultRead:
    file_hash = hashlib.sha256(contents).hexdigest()
    if session.scalar(
        select(ImportJob.id).where(
            ImportJob.portfolio_id == portfolio.id,
            ImportJob.file_sha256 == file_hash,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This file has already been imported into this portfolio.",
        )

    parsed = parse_csv_balances(contents, mapping)
    safe_filename = PurePosixPath(filename.replace("\\", "/")).name[:255] or "balances.csv"
    source_label = (source_name or "").strip() or safe_filename[:160]
    if len(source_label) > 160 or any(ord(character) < 32 for character in source_label):
        raise ValueError(
            "The account name must be 160 characters or fewer without control characters."
        )
    imported_at = datetime.now(UTC)
    if source_id is None:
        duplicate = session.scalar(
            select(Source.id).where(
                Source.portfolio_id == portfolio.id,
                Source.kind == "exchange_balance_import",
                func.lower(Source.name) == source_label.lower(),
            )
        )
        if duplicate:
            raise HTTPException(
                status_code=409,
                detail=(
                    "A balance source with this name already exists. "
                    "Select it to add a new snapshot."
                ),
            )
        source = Source(
            portfolio_id=portfolio.id,
            kind="exchange_balance_import",
            name=source_label,
            quality_status=QualityStatus.NEEDS_REVIEW.value,
            retrieved_at=imported_at,
        )
        session.add(source)
        try:
            session.flush()
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(
                status_code=409,
                detail=(
                    "A balance source with this name already exists. "
                    "Select it to add a new snapshot."
                ),
            ) from exc
    else:
        source = session.scalar(
            select(Source).where(
                Source.id == source_id,
                Source.portfolio_id == portfolio.id,
                Source.kind == "exchange_balance_import",
            )
        )
        if source is None:
            raise HTTPException(status_code=404, detail="Balance source not found.")
        source.quality_status = QualityStatus.NEEDS_REVIEW.value
        source.retrieved_at = imported_at

    warnings = list(parsed.warnings)
    warnings.append(
        "These imported balances are not chain-verified. PocketOrbit shows their known value "
        "separately and keeps the portfolio total partial."
    )
    snapshot = WalletSnapshot(
        source_id=source.id,
        retrieved_at=imported_at,
        quote_currency=portfolio.reporting_currency,
        known_value=0,
        total_value=None,
        quality_status=QualityStatus.NEEDS_REVIEW.value,
        coverage="csv_balance_statement",
        warnings=list(dict.fromkeys(warnings)),
    )
    session.add(snapshot)
    session.flush()

    for row in parsed.accepted:
        asset = _resolve_or_create_asset(session, portfolio.id, source.id, row)
        session.add(
            Balance(
                source_id=source.id,
                snapshot_id=snapshot.id,
                asset_id=asset.id,
                quantity=row.quantity,
                quality_status=QualityStatus.NEEDS_REVIEW.value,
                source_record_id=f"row:{row.row_number}",
                retrieved_at=imported_at,
            )
        )

    rejected_count = parsed.rows_received - len(parsed.accepted)
    job = ImportJob(
        portfolio_id=portfolio.id,
        source_id=source.id,
        snapshot_id=snapshot.id,
        filename=safe_filename,
        file_sha256=file_hash,
        status="needs_review",
        rows_received=parsed.rows_received,
        rows_accepted=len(parsed.accepted),
        rows_rejected=rejected_count,
    )
    session.add(job)
    try:
        session.flush()
        record_valuation_snapshot(session, portfolio)
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This file or one of its balance rows has already been imported.",
        ) from exc

    return ImportResultRead(
        import_id=str(job.id),
        source_id=str(source.id),
        filename=safe_filename,
        rows_received=parsed.rows_received,
        rows_accepted=len(parsed.accepted),
        rows_rejected=rejected_count,
        unmatched_assets=list(parsed.unmatched_assets),
        warnings=list(dict.fromkeys(warnings)),
        rejected_rows=list(parsed.rejected),
    )
