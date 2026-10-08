import hashlib
from pathlib import PurePosixPath
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.connectors.exchanges.csv.normalizer import parse_csv_transactions
from app.models.activity import Transaction
from app.models.asset import Asset
from app.models.import_job import ImportJob
from app.models.portfolio import Portfolio
from app.models.source import Source
from app.schemas.imports import CsvFieldMapping, ImportResultRead
from app.services.asset_service import get_or_create_asset
from app.services.persistent_portfolios import record_valuation_snapshot

NATIVE_ASSETS = {
    ("solana", "SOL"): ("solana", "Solana", 9),
    ("ethereum", "ETH"): ("ethereum:native", "Ether", 18),
    ("base", "ETH"): ("base:native", "Ether", 18),
    ("arbitrum", "ETH"): ("arbitrum:native", "Ether", 18),
}


def import_csv_transactions(
    session: Session,
    portfolio: Portfolio,
    filename: str,
    contents: bytes,
    mapping: CsvFieldMapping,
) -> ImportResultRead:
    file_hash = hashlib.sha256(contents).hexdigest()
    prior_import = session.scalar(
        select(ImportJob).where(
            ImportJob.portfolio_id == portfolio.id,
            ImportJob.file_sha256 == file_hash,
        )
    )
    if prior_import:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This file has already been imported into this portfolio.",
        )

    parsed = parse_csv_transactions(contents, mapping)
    safe_filename = PurePosixPath(filename.replace("\\", "/")).name[:255] or "exchange.csv"
    source = Source(
        portfolio_id=portfolio.id,
        kind="exchange_import",
        name=safe_filename[:160],
        quality_status="partial",
    )
    session.add(source)
    session.flush()
    if portfolio.import_history_started_at is None:
        portfolio.import_history_started_at = source.created_at

    for row in parsed.accepted:
        asset = _resolve_or_create_asset(session, portfolio.id, source.id, row)
        session.add(
            Transaction(
                source_id=source.id,
                asset_id=asset.id,
                source_record_id=row.source_record_id,
                kind=row.kind,
                quantity=row.quantity,
                occurred_at=row.occurred_at,
                # CSV rows are user-provided records, not independently verified transactions.
                quality_status="needs_review",
            )
        )

    rows_rejected = parsed.rows_received - len(parsed.accepted)
    warnings = list(parsed.warnings)
    warnings.append(
        "Imported rows are transaction history, not a current account statement; holdings may be "
        "partial until a complete history is included."
    )
    if parsed.unmatched_assets:
        warnings.append(
            "Ticker-only assets stay separate and unpriced until their identity is confirmed."
        )

    job = ImportJob(
        portfolio_id=portfolio.id,
        source_id=source.id,
        filename=safe_filename,
        file_sha256=file_hash,
        status="needs_review" if rows_rejected or parsed.unmatched_assets else "completed",
        rows_received=parsed.rows_received,
        rows_accepted=len(parsed.accepted),
        rows_rejected=rows_rejected,
    )
    source.retrieved_at = None
    session.add(job)
    try:
        session.flush()
        record_valuation_snapshot(session, portfolio)
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="One or more transaction IDs already exist in this import.",
        ) from exc

    return ImportResultRead(
        import_id=str(job.id),
        source_id=str(source.id),
        filename=safe_filename,
        rows_received=parsed.rows_received,
        rows_accepted=len(parsed.accepted),
        rows_rejected=rows_rejected,
        unmatched_assets=list(parsed.unmatched_assets),
        warnings=list(dict.fromkeys(warnings)),
        rejected_rows=list(parsed.rejected),
    )


def _resolve_or_create_asset(
    session: Session,
    portfolio_id: UUID,
    source_id: UUID,
    row,
) -> Asset:
    if row.contract_address and row.network_id:
        contract_address = (
            row.contract_address if row.network_id == "solana" else row.contract_address.lower()
        )
        canonical_id = f"{row.network_id}:{contract_address}"
        return get_or_create_asset(
            session,
            canonical_id=canonical_id,
            symbol=row.symbol,
            name=f"Unverified {row.symbol}",
            network_id=row.network_id,
            contract_address=contract_address,
            decimals=18,
        )

    native_asset = NATIVE_ASSETS.get((row.network_id or "", row.symbol))
    if native_asset:
        canonical_id, name, decimals = native_asset
        return get_or_create_asset(
            session,
            canonical_id=canonical_id,
            symbol=row.symbol,
            name=name,
            network_id=row.network_id,
            contract_address=None,
            decimals=decimals,
        )

    canonical_id = (
        f"import:{portfolio_id}:{source_id}:{row.network_id or 'unknown'}:{row.symbol}"
    )
    return get_or_create_asset(
        session,
        canonical_id=canonical_id,
        symbol=row.symbol,
        name=f"Unmatched {row.symbol}",
        network_id=row.network_id,
        contract_address=None,
        decimals=18,
    )
