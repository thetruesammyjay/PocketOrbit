import hashlib
import re
from datetime import UTC, datetime
from pathlib import PurePosixPath
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
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
    *,
    source_name: str | None = None,
    history_complete: bool = False,
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
    source_label = (source_name or "").strip() or safe_filename[:160]
    if len(source_label) > 160 or any(ord(character) < 32 for character in source_label):
        raise ValueError("The exchange or account name must be 160 characters or fewer.")
    source = session.scalar(
        select(Source).where(
            Source.portfolio_id == portfolio.id,
            Source.kind == "exchange_import",
            func.lower(Source.name) == source_label.casefold(),
        )
    )
    if source is None:
        source = Source(
            portfolio_id=portfolio.id,
            kind="exchange_import",
            name=source_label,
            quality_status="partial",
            retrieved_at=datetime.now(UTC),
        )
        session.add(source)
        session.flush()
    else:
        source.retrieved_at = datetime.now(UTC)
        source.quality_status = "partial"
    if portfolio.import_history_started_at is None:
        portfolio.import_history_started_at = source.created_at

    job = ImportJob(
        portfolio_id=portfolio.id,
        source_id=source.id,
        filename=safe_filename,
        file_sha256=file_hash,
        status="received",
        rows_received=parsed.rows_received,
        rows_accepted=0,
        rows_rejected=0,
        history_complete=False,
    )
    session.add(job)
    session.flush()

    duplicate_count = 0
    accepted_count = 0
    for row in parsed.accepted:
        asset = _resolve_or_create_asset(session, portfolio.id, source.id, row)
        dedupe_asset_key = (
            asset.canonical_id
            if row.contract_address or (row.network_id or "", row.symbol) in NATIVE_ASSETS
            else f"unverified:{row.network_id or 'unknown'}:{row.symbol}"
        )
        dedupe_key = _transaction_dedupe_key(source_label, dedupe_asset_key, row)
        if session.scalar(select(Transaction.id).where(Transaction.dedupe_key == dedupe_key)):
            duplicate_count += 1
            continue

        fee_asset = (
            _resolve_or_create_asset(
                session,
                portfolio.id,
                source.id,
                row,
                symbol=row.fee_symbol,
            )
            if row.fee_quantity is not None and row.fee_symbol
            else None
        )
        session.add(
            Transaction(
                source_id=source.id,
                import_job_id=job.id,
                asset_id=asset.id,
                source_record_id=row.source_record_id,
                external_record_id=row.external_record_id,
                dedupe_key=dedupe_key,
                transaction_hash=row.transaction_hash,
                kind=row.kind,
                quantity=row.quantity,
                fee_quantity=row.fee_quantity,
                fee_asset_id=fee_asset.id if fee_asset else None,
                quote_amount=row.quote_amount,
                quote_currency=row.quote_currency,
                occurred_at=row.occurred_at,
                # CSV rows are user-provided records, not independently verified transactions.
                quality_status="needs_review",
            )
        )
        accepted_count += 1

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
    if duplicate_count:
        warnings.append(f"Skipped {duplicate_count} row(s) already imported from this account.")
    effective_history_complete = history_complete and rows_rejected == 0
    if history_complete and rows_rejected:
        warnings.append(
            "History was not marked complete because some rows were rejected. Resolve the rows "
            "and import the corrected file before relying on performance results."
        )
    elif history_complete:
        warnings.append(
            "You marked this export as the full available history for this account. PocketOrbit "
            "cannot independently verify that the exchange export omitted no records."
        )

    coverage_start = min((row.occurred_at for row in parsed.accepted), default=None)
    coverage_end = max((row.occurred_at for row in parsed.accepted), default=None)

    job.status = (
        "needs_review"
        if accepted_count or rows_rejected or parsed.unmatched_assets
        else "completed"
    )
    job.rows_accepted = accepted_count
    job.rows_rejected = rows_rejected
    job.rows_duplicate = duplicate_count
    job.coverage_start_at = coverage_start
    job.coverage_end_at = coverage_end
    job.history_complete = effective_history_complete
    source.retrieved_at = datetime.now(UTC)
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
        rows_accepted=accepted_count,
        rows_rejected=rows_rejected,
        rows_duplicate=duplicate_count,
        unmatched_assets=list(parsed.unmatched_assets),
        warnings=list(dict.fromkeys(warnings)),
        rejected_rows=list(parsed.rejected),
        coverage_start_at=coverage_start,
        coverage_end_at=coverage_end,
        history_complete=effective_history_complete,
    )


def _resolve_or_create_asset(
    session: Session,
    portfolio_id: UUID,
    source_id: UUID,
    row,
    *,
    symbol: str | None = None,
) -> Asset:
    asset_symbol = symbol or row.symbol
    if not symbol and row.contract_address and row.network_id:
        contract_address = (
            row.contract_address if row.network_id == "solana" else row.contract_address.lower()
        )
        canonical_id = f"{row.network_id}:{contract_address}"
        return get_or_create_asset(
            session,
            canonical_id=canonical_id,
            symbol=asset_symbol,
            name=f"Unverified {asset_symbol}",
            network_id=row.network_id,
            contract_address=contract_address,
            decimals=18,
        )

    native_asset = NATIVE_ASSETS.get((row.network_id or "", asset_symbol))
    if native_asset:
        canonical_id, name, decimals = native_asset
        return get_or_create_asset(
            session,
            canonical_id=canonical_id,
            symbol=asset_symbol,
            name=name,
            network_id=row.network_id,
            contract_address=None,
            decimals=decimals,
        )

    canonical_id = f"import:{portfolio_id}:{source_id}:{row.network_id or 'unknown'}:{asset_symbol}"
    return get_or_create_asset(
        session,
        canonical_id=canonical_id,
        symbol=asset_symbol,
        name=f"Unmatched {asset_symbol}",
        network_id=row.network_id,
        contract_address=None,
        decimals=18,
    )


def _transaction_dedupe_key(source_name: str, canonical_asset: str, row) -> str:
    scope = re.sub(r"\s+", " ", source_name.strip().casefold())
    identifier = row.transaction_hash or row.external_record_id or ""
    fields = [scope, identifier, canonical_asset, row.kind, str(row.quantity)]
    fields.append(row.occurred_at.isoformat())
    fields.extend((str(row.fee_quantity or ""), str(row.fee_symbol or "")))
    identity = "|".join(fields)
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()
