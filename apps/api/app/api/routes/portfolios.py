import json
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.connectors.base import ProviderNotConfiguredError, ProviderRequestError
from app.core.database import get_db
from app.core.rate_limit import enforce_rate_limit, request_client_ip
from app.core.security import get_current_user
from app.models.activity import Transaction
from app.models.asset import Asset
from app.models.balance import Balance
from app.models.import_job import ImportJob
from app.models.source import Source
from app.models.sync_job import SyncJob
from app.models.transfer_match import TransferMatch
from app.models.user import User
from app.models.wallet_snapshot import WalletSnapshot
from app.schemas.activity import ActivityRead
from app.schemas.common import QualityStatus
from app.schemas.imports import (
    CsvBalanceFieldMapping,
    CsvFieldMapping,
    ImportJobRead,
    ImportResultRead,
    PerformanceRead,
    TransactionReview,
    TransferMatchRead,
    TransferReview,
)
from app.schemas.portfolio import PortfolioCreate, PortfolioRead, PortfolioSummaryRead
from app.schemas.source import SourceRead, WalletSourceCreate
from app.schemas.wallet import WalletSyncResponse
from app.services.csv_balance_import_service import import_csv_balance_statement
from app.services.csv_import_service import import_csv_transactions
from app.services.import_pricing_service import price_imported_assets
from app.services.performance_service import get_portfolio_performance
from app.services.persistent_portfolios import (
    _activity_kind,
    create_user_portfolio,
    get_portfolio_summary,
    latest_sync_warnings,
    list_user_portfolios,
    record_valuation_snapshot,
    require_owned_portfolio,
)
from app.services.portfolio_service import get_demo_portfolio_summary
from app.services.transfer_matching import list_transfer_matches, refresh_transfer_suggestions
from app.services.wallet_persistence import save_wallet_snapshot
from app.services.wallet_service import refresh_public_wallet

router = APIRouter()


@router.get("/demo/summary")
def demo_portfolio_summary() -> dict[str, object]:
    """Return a deterministic sample portfolio, never live account data."""
    return get_demo_portfolio_summary()


@router.get("", response_model=list[PortfolioRead])
def portfolios(
    session: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[PortfolioRead]:
    return list_user_portfolios(session, user)


@router.post("", response_model=PortfolioRead, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    payload: PortfolioCreate,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PortfolioRead:
    return create_user_portfolio(session, user, payload)


@router.get("/{portfolio_id}/summary", response_model=PortfolioSummaryRead)
def portfolio_summary(
    portfolio_id: UUID,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PortfolioSummaryRead:
    portfolio = require_owned_portfolio(session, user, portfolio_id)
    return get_portfolio_summary(session, portfolio)


@router.get("/{portfolio_id}/sources", response_model=list[SourceRead])
def portfolio_sources(
    portfolio_id: UUID,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[SourceRead]:
    require_owned_portfolio(session, user, portfolio_id)
    sources = session.scalars(
        select(Source).where(Source.portfolio_id == portfolio_id).order_by(Source.created_at)
    ).all()
    source_ids = [source.id for source in sources]
    sync_warnings = latest_sync_warnings(session, source_ids)
    if source_ids:
        ranked_snapshots = (
            select(
                WalletSnapshot.id.label("snapshot_id"),
                func.row_number()
                .over(
                    partition_by=WalletSnapshot.source_id,
                    order_by=(WalletSnapshot.retrieved_at.desc(), WalletSnapshot.id.desc()),
                )
                .label("snapshot_rank"),
            )
            .where(WalletSnapshot.source_id.in_(source_ids))
            .subquery()
        )
        snapshots = session.scalars(
            select(WalletSnapshot)
            .join(ranked_snapshots, WalletSnapshot.id == ranked_snapshots.c.snapshot_id)
            .where(ranked_snapshots.c.snapshot_rank == 1)
        ).all()
    else:
        snapshots = []
    latest_snapshot_by_source: dict[UUID, WalletSnapshot] = {}
    for snapshot in snapshots:
        latest_snapshot_by_source.setdefault(snapshot.source_id, snapshot)
    return [
        SourceRead(
            id=str(source.id),
            name=source.name,
            kind=source.kind,
            network=source.network_id,
            address_label=_mask_address(source.public_address),
            last_updated_at=source.retrieved_at,
            quality=source.quality_status,
            coverage=(
                latest_snapshot_by_source[source.id].coverage
                if source.id in latest_snapshot_by_source
                else None
            ),
            warnings=(
                [
                    *(
                        latest_snapshot_by_source[source.id].warnings
                        if source.id in latest_snapshot_by_source
                        else []
                    ),
                    *([sync_warnings[source.id]] if source.id in sync_warnings else []),
                ]
            ),
        )
        for source in sources
    ]


@router.post(
    "/{portfolio_id}/sources/wallets",
    response_model=WalletSyncResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_wallet_source(
    portfolio_id: UUID,
    payload: WalletSourceCreate,
    request: Request,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WalletSyncResponse:
    enforce_rate_limit(
        session,
        scope="wallet-sync-account",
        subject=str(user.id),
        max_requests=60,
        window_seconds=3600,
    )
    enforce_rate_limit(
        session,
        scope="wallet-sync-ip",
        subject=request_client_ip(request),
        max_requests=120,
        window_seconds=3600,
    )
    portfolio = require_owned_portfolio(session, user, portfolio_id)
    duplicate = session.scalar(
        select(Source.id).where(
            Source.portfolio_id == portfolio_id,
            Source.kind == "wallet",
            Source.network_id == payload.network,
            Source.public_address == payload.address,
        )
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="This wallet is already connected."
        )

    source = Source(
        portfolio_id=portfolio.id,
        kind="wallet",
        name=payload.name,
        network_id=payload.network,
        public_address=payload.address,
        quality_status=QualityStatus.OFFLINE.value,
        retrieved_at=None,
    )
    session.add(source)
    try:
        session.flush()
        sync_job = SyncJob(source_id=source.id, status="queued")
        session.add(sync_job)
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This wallet is already connected.",
        ) from exc

    try:
        result = await _sync_wallet(payload.network, payload.address, portfolio.reporting_currency)
    except HTTPException as exc:
        if exc.status_code not in {
            status.HTTP_502_BAD_GATEWAY,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        }:
            _mark_sync_failed(
                session,
                source,
                sync_job,
                f"Wallet sync failed with HTTP {exc.status_code}.",
            )
            raise
        message = exc.detail if isinstance(exc.detail, str) else "Live wallet data is unavailable."
        sync_job.status = "failed"
        sync_job.message = message[:512]
        session.commit()
        return WalletSyncResponse(
            network=payload.network,
            network_name=_network_name(payload.network),
            coverage="not_synced",
            address=payload.address,
            is_live=False,
            is_persisted=True,
            source_id=str(source.id),
            snapshot_id=None,
            retrieved_at=datetime.now(UTC),
            quote_currency=portfolio.reporting_currency,
            total_value=None,
            known_value=Decimal("0"),
            quality=QualityStatus.OFFLINE,
            balances=[],
            warnings=[message],
        )
    except Exception:
        _mark_sync_failed(session, source, sync_job, "Wallet sync failed unexpectedly.")
        raise

    snapshot = save_wallet_snapshot(session, portfolio, source, result)
    sync_job.status = "completed"
    sync_job.message = "Wallet snapshot saved."
    session.commit()
    return result.model_copy(
        update={
            "is_persisted": True,
            "source_id": str(source.id),
            "snapshot_id": str(snapshot.id),
        }
    )


@router.post(
    "/{portfolio_id}/sources/{source_id}/sync",
    response_model=WalletSyncResponse,
)
async def sync_wallet_source(
    portfolio_id: UUID,
    source_id: UUID,
    request: Request,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WalletSyncResponse:
    enforce_rate_limit(
        session,
        scope="wallet-sync-account",
        subject=str(user.id),
        max_requests=60,
        window_seconds=3600,
    )
    enforce_rate_limit(
        session,
        scope="wallet-sync-ip",
        subject=request_client_ip(request),
        max_requests=120,
        window_seconds=3600,
    )
    portfolio = require_owned_portfolio(session, user, portfolio_id)
    source = session.scalar(
        select(Source).where(
            Source.id == source_id,
            Source.portfolio_id == portfolio_id,
            Source.kind == "wallet",
        )
    )
    if not source or not source.network_id or not source.public_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet source not found."
        )

    sync_job = SyncJob(source_id=source.id, status="queued")
    session.add(sync_job)
    session.commit()

    try:
        result = await _sync_wallet(
            source.network_id, source.public_address, portfolio.reporting_currency
        )
    except HTTPException as exc:
        if exc.status_code not in {
            status.HTTP_502_BAD_GATEWAY,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        }:
            _mark_sync_failed(
                session,
                source,
                sync_job,
                f"Wallet sync failed with HTTP {exc.status_code}.",
            )
            raise
        message = exc.detail if isinstance(exc.detail, str) else "Live wallet data is unavailable."
        source.quality_status = QualityStatus.OFFLINE.value
        sync_job.status = "failed"
        sync_job.message = message[:512]
        session.commit()
        raise
    except Exception:
        _mark_sync_failed(session, source, sync_job, "Wallet sync failed unexpectedly.")
        raise

    snapshot = save_wallet_snapshot(session, portfolio, source, result)
    sync_job.status = "completed"
    sync_job.message = "Wallet snapshot saved."
    session.commit()
    return result.model_copy(
        update={
            "is_persisted": True,
            "source_id": str(source.id),
            "snapshot_id": str(snapshot.id),
        }
    )


@router.delete(
    "/{portfolio_id}/sources/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_wallet_source(
    portfolio_id: UUID,
    source_id: UUID,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    portfolio = require_owned_portfolio(session, user, portfolio_id)
    source = session.scalar(
        select(Source).where(
            Source.id == source_id,
            Source.portfolio_id == portfolio_id,
            Source.kind == "wallet",
        )
    )
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet source not found."
        )

    _delete_transaction_rows(
        session, select(Transaction.id).where(Transaction.source_id == source.id)
    )
    session.execute(delete(Transaction).where(Transaction.source_id == source.id))
    session.execute(delete(Balance).where(Balance.source_id == source.id))
    session.execute(delete(WalletSnapshot).where(WalletSnapshot.source_id == source.id))
    session.execute(delete(SyncJob).where(SyncJob.source_id == source.id))
    session.delete(source)
    session.flush()
    record_valuation_snapshot(session, portfolio)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def _sync_wallet(network: str, address: str, currency: str) -> WalletSyncResponse:
    try:
        return await refresh_public_wallet(network, address, currency)
    except ProviderNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except ProviderRequestError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


def _mark_sync_failed(session: Session, source: Source, sync_job: SyncJob, message: str) -> None:
    source.quality_status = QualityStatus.OFFLINE.value
    sync_job.status = "failed"
    sync_job.message = message[:512]
    session.commit()


def _mask_address(value: str | None) -> str | None:
    if not value:
        return None
    return f"{value[:6]}…{value[-4:]}" if len(value) > 12 else f"{value[:3]}…{value[-3:]}"


def _network_name(network_id: str) -> str:
    return {
        "solana": "Solana",
        "ethereum": "Ethereum",
        "base": "Base",
        "arbitrum": "Arbitrum One",
    }.get(network_id, network_id)


@router.post(
    "/{portfolio_id}/imports",
    response_model=ImportResultRead,
    status_code=status.HTTP_201_CREATED,
)
async def import_transactions(
    portfolio_id: UUID,
    file: UploadFile = File(...),
    mapping_json: str = Form(..., alias="mapping"),
    mode: str = Form(default="transactions"),
    balance_source_id: str = Form(default="", alias="balanceSourceId"),
    balance_source_name: str = Form(default="", alias="balanceSourceName"),
    transaction_source_name: str = Form(default="", alias="transactionSourceName"),
    history_complete: bool = Form(default=False, alias="historyComplete"),
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ImportResultRead:
    enforce_rate_limit(
        session,
        scope="csv-import-account",
        subject=str(user.id),
        max_requests=12,
        window_seconds=3600,
    )
    portfolio = require_owned_portfolio(session, user, portfolio_id)
    filename = file.filename or "exchange.csv"
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=415, detail="Upload a CSV file to import transactions.")
    contents = await file.read(5 * 1024 * 1024 + 1)
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="The import limit is 5 MB.")
    try:
        if mode == "transactions":
            mapping = CsvFieldMapping.model_validate(json.loads(mapping_json))
            result = import_csv_transactions(
                session,
                portfolio,
                filename,
                contents,
                mapping,
                source_name=transaction_source_name,
                history_complete=history_complete,
            )
        elif mode == "balances":
            mapping = CsvBalanceFieldMapping.model_validate(json.loads(mapping_json))
            result = import_csv_balance_statement(
                session,
                portfolio,
                filename,
                contents,
                mapping,
                source_id=UUID(balance_source_id) if balance_source_id else None,
                source_name=balance_source_name,
            )
        else:
            raise ValueError("Choose transaction history or a current balance statement.")
        try:
            price_warnings = await price_imported_assets(session, portfolio, UUID(result.source_id))
            if price_warnings:
                result = result.model_copy(
                    update={"warnings": list(dict.fromkeys(result.warnings + price_warnings))}
                )
        except Exception:
            # The transaction import is already committed; an optional quote failure must
            # not make the client believe the import failed and retry a saved file.
            session.rollback()
            result = result.model_copy(
                update={
                    "warnings": list(
                        dict.fromkeys(
                            result.warnings
                            + ["Current prices could not be refreshed. Review prices later."]
                        )
                    )
                }
            )
        return result
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="The column mapping is invalid.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{portfolio_id}/imports", response_model=list[ImportJobRead])
def portfolio_imports(
    portfolio_id: UUID,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ImportJobRead]:
    require_owned_portfolio(session, user, portfolio_id)
    jobs = session.scalars(
        select(ImportJob)
        .where(ImportJob.portfolio_id == portfolio_id)
        .order_by(ImportJob.created_at.desc())
        .limit(100)
    ).all()
    return [
        ImportJobRead(
            id=str(job.id),
            filename=job.filename,
            status=job.status,
            rows_received=job.rows_received,
            rows_accepted=job.rows_accepted,
            rows_rejected=job.rows_rejected,
            rows_duplicate=job.rows_duplicate,
            created_at=job.created_at,
            coverage_start_at=job.coverage_start_at,
            coverage_end_at=job.coverage_end_at,
            history_complete=job.history_complete,
        )
        for job in jobs
    ]


@router.delete("/{portfolio_id}/imports/{import_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_import(
    portfolio_id: UUID,
    import_id: UUID,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    portfolio = require_owned_portfolio(session, user, portfolio_id)
    job = session.scalar(
        select(ImportJob).where(
            ImportJob.id == import_id,
            ImportJob.portfolio_id == portfolio_id,
        )
    )
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import not found.")

    source = session.get(Source, job.source_id) if job.source_id else None
    if source is not None:
        if source.portfolio_id != portfolio_id or source.kind not in {
            "exchange_import",
            "exchange_balance_import",
        }:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="This import cannot be removed."
            )
        if source.kind == "exchange_balance_import":
            if job.snapshot_id:
                session.execute(delete(Balance).where(Balance.snapshot_id == job.snapshot_id))
                session.execute(
                    delete(WalletSnapshot).where(
                        WalletSnapshot.id == job.snapshot_id,
                        WalletSnapshot.source_id == source.id,
                    )
                )
        else:
            _delete_transaction_rows(
                session,
                select(Transaction.id).where(Transaction.import_job_id == job.id),
            )
            session.execute(delete(Transaction).where(Transaction.import_job_id == job.id))
            session.execute(delete(Balance).where(Balance.source_id == source.id))
            session.execute(delete(WalletSnapshot).where(WalletSnapshot.source_id == source.id))
    session.delete(job)
    session.flush()
    if source is not None:
        remaining_jobs = session.scalar(
            select(ImportJob.id).where(ImportJob.source_id == source.id).limit(1)
        )
        if remaining_jobs is None:
            _delete_transaction_rows(
                session,
                select(Transaction.id).where(Transaction.source_id == source.id),
            )
            session.execute(delete(Transaction).where(Transaction.source_id == source.id))
            session.execute(delete(Balance).where(Balance.source_id == source.id))
            session.execute(delete(WalletSnapshot).where(WalletSnapshot.source_id == source.id))
            session.delete(source)
            session.flush()
    record_valuation_snapshot(session, portfolio)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{portfolio_id}/transfers", response_model=list[TransferMatchRead])
def portfolio_transfers(
    portfolio_id: UUID,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[TransferMatchRead]:
    portfolio = require_owned_portfolio(session, user, portfolio_id)
    refresh_transfer_suggestions(session, portfolio)
    session.commit()
    return list_transfer_matches(session, portfolio)


@router.get("/{portfolio_id}/activity", response_model=list[ActivityRead])
def portfolio_activity(
    portfolio_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ActivityRead]:
    portfolio = require_owned_portfolio(session, user, portfolio_id)
    source_rows = session.scalars(select(Source).where(Source.portfolio_id == portfolio.id)).all()
    source_by_id = {source.id: source for source in source_rows}
    if not source_by_id:
        return []
    transactions = session.scalars(
        select(Transaction)
        .where(Transaction.source_id.in_(source_by_id))
        .order_by(Transaction.occurred_at.desc(), Transaction.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    if not transactions:
        return []
    assets = session.scalars(
        select(Asset).where(Asset.id.in_({transaction.asset_id for transaction in transactions}))
    ).all()
    asset_by_id = {asset.id: asset for asset in assets}
    transaction_ids = [transaction.id for transaction in transactions]
    matches = session.scalars(
        select(TransferMatch).where(
            TransferMatch.outgoing_transaction_id.in_(transaction_ids)
            | TransferMatch.incoming_transaction_id.in_(transaction_ids)
        )
    ).all()
    transfer_status: dict[UUID, str] = {}
    for match in matches:
        transfer_status[match.outgoing_transaction_id] = match.status
        transfer_status[match.incoming_transaction_id] = match.status
    return [
        ActivityRead(
            id=str(transaction.id),
            kind=_activity_kind(transaction.kind),
            asset_symbol=asset_by_id[transaction.asset_id].symbol
            if transaction.asset_id in asset_by_id
            else "Unknown",
            quantity=abs(transaction.quantity),
            source_name=source_by_id[transaction.source_id].name,
            occurred_at=transaction.occurred_at,
            status=(
                transaction.quality_status
                if transaction.quality_status in {"user_confirmed", "rejected"}
                else "confirmed"
                if transaction.quality_status == "fresh"
                else "needs_review"
            ),
            transaction_hash=transaction.transaction_hash,
            external_record_id=transaction.external_record_id,
            quote_amount=transaction.quote_amount,
            quote_currency=transaction.quote_currency,
            transfer_status=transfer_status.get(transaction.id),
        )
        for transaction in transactions
    ]


@router.post("/{portfolio_id}/transfers/{match_id}/review", response_model=TransferMatchRead)
def review_transfer(
    portfolio_id: UUID,
    match_id: UUID,
    payload: TransferReview,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TransferMatchRead:
    portfolio = require_owned_portfolio(session, user, portfolio_id)
    match = session.scalar(
        select(TransferMatch).where(
            TransferMatch.id == match_id,
            TransferMatch.portfolio_id == portfolio.id,
        )
    )
    if match is None:
        raise HTTPException(status_code=404, detail="Transfer suggestion not found.")
    if match.status != "suggested":
        raise HTTPException(
            status_code=409, detail="This transfer suggestion has already been reviewed."
        )
    match.status = "matched" if payload.accepted else "rejected"
    match.reviewed_at = datetime.now(UTC)
    if payload.accepted:
        alternatives = session.scalars(
            select(TransferMatch).where(
                TransferMatch.portfolio_id == portfolio.id,
                TransferMatch.id != match.id,
                TransferMatch.status == "suggested",
                (
                    TransferMatch.outgoing_transaction_id.in_(
                        [match.outgoing_transaction_id, match.incoming_transaction_id]
                    )
                )
                | (
                    TransferMatch.incoming_transaction_id.in_(
                        [match.outgoing_transaction_id, match.incoming_transaction_id]
                    )
                ),
            )
        ).all()
        for alternative in alternatives:
            alternative.status = "rejected"
            alternative.reviewed_at = datetime.now(UTC)
            alternative.rationale = (
                "Closed because one of these records was confirmed in another transfer match."
            )
    session.commit()
    return next(
        item for item in list_transfer_matches(session, portfolio) if item.id == str(match.id)
    )


@router.post(
    "/{portfolio_id}/activity/{transaction_id}/review", status_code=status.HTTP_204_NO_CONTENT
)
def review_transaction(
    portfolio_id: UUID,
    transaction_id: UUID,
    payload: TransactionReview,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    portfolio = require_owned_portfolio(session, user, portfolio_id)
    source_ids = select(Source.id).where(Source.portfolio_id == portfolio.id)
    transaction = session.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.source_id.in_(source_ids),
        )
    )
    if transaction is None:
        raise HTTPException(status_code=404, detail="Activity record not found.")
    if transaction.quality_status not in {"needs_review", "user_confirmed", "rejected"}:
        raise HTTPException(status_code=409, detail="This activity record cannot be reviewed.")
    transaction.quality_status = "user_confirmed" if payload.accepted else "rejected"
    session.flush()
    refresh_transfer_suggestions(session, portfolio)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{portfolio_id}/performance", response_model=PerformanceRead)
def portfolio_performance(
    portfolio_id: UUID,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PerformanceRead:
    portfolio = require_owned_portfolio(session, user, portfolio_id)
    refresh_transfer_suggestions(session, portfolio)
    session.flush()
    return get_portfolio_performance(session, portfolio)


def _delete_transaction_rows(session: Session, transaction_ids) -> None:
    session.execute(
        delete(TransferMatch).where(
            TransferMatch.outgoing_transaction_id.in_(transaction_ids)
            | TransferMatch.incoming_transaction_id.in_(transaction_ids)
        )
    )
