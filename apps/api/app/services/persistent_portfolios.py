from collections import defaultdict
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.calculations.allocation import allocation_percentages
from app.models.activity import Transaction
from app.models.asset import Asset
from app.models.balance import Balance
from app.models.portfolio import Portfolio
from app.models.price import Price
from app.models.source import Source
from app.models.sync_job import SyncJob
from app.models.transfer_match import TransferMatch
from app.models.user import User
from app.models.valuation import ValuationSnapshot
from app.models.wallet_snapshot import WalletSnapshot
from app.schemas.activity import ActivityRead
from app.schemas.common import QualityStatus
from app.schemas.portfolio import (
    AllocationRead,
    HoldingProvenance,
    HoldingRead,
    PortfolioCreate,
    PortfolioRead,
    PortfolioSummaryRead,
)
from app.schemas.source import SourceRead

ALLOCATION_COLORS = ("#6757E8", "#48A8E0", "#16A875", "#E9B949", "#EF775B", "#8A76D6")
SOURCE_STALE_AFTER = timedelta(hours=24)
PRICE_STALE_AFTER = timedelta(minutes=10)
INCOMPLETE_QUALITIES = {
    QualityStatus.PARTIAL,
    QualityStatus.NEEDS_REVIEW,
    QualityStatus.UNMATCHED,
    QualityStatus.OFFLINE,
}


def list_user_portfolios(session: Session, user: User) -> list[PortfolioRead]:
    portfolios = session.scalars(
        select(Portfolio).where(Portfolio.user_id == user.id).order_by(Portfolio.created_at)
    ).all()
    return [_portfolio_read(portfolio) for portfolio in portfolios]


def create_user_portfolio(session: Session, user: User, payload: PortfolioCreate) -> PortfolioRead:
    portfolio = Portfolio(
        user_id=user.id,
        name=payload.name.strip(),
        reporting_currency=payload.reporting_currency,
    )
    session.add(portfolio)
    session.commit()
    session.refresh(portfolio)
    return _portfolio_read(portfolio)


def require_owned_portfolio(session: Session, user: User, portfolio_id: UUID) -> Portfolio:
    portfolio = session.scalar(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == user.id)
    )
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found.")
    return portfolio


def latest_sync_warnings(session: Session, source_ids: list[UUID]) -> dict[UUID, str]:
    if not source_ids:
        return {}
    ranked_jobs = (
        select(
            SyncJob.id.label("job_id"),
            func.row_number()
            .over(
                partition_by=SyncJob.source_id,
                order_by=(SyncJob.created_at.desc(), SyncJob.id.desc()),
            )
            .label("job_rank"),
        )
        .where(SyncJob.source_id.in_(source_ids))
        .subquery()
    )
    latest_jobs = session.scalars(
        select(SyncJob)
        .join(ranked_jobs, SyncJob.id == ranked_jobs.c.job_id)
        .where(ranked_jobs.c.job_rank == 1)
    ).all()
    warnings: dict[UUID, str] = {}
    for job in latest_jobs:
        if job.status == "failed":
            warnings[job.source_id] = job.message or "The last wallet sync failed."
        elif job.status in {"queued", "running"}:
            warnings[job.source_id] = "A wallet sync has not completed."
    return warnings


def record_valuation_snapshot(session: Session, portfolio: Portfolio) -> None:
    summary = _build_portfolio_summary(session, portfolio)
    session.add(
        ValuationSnapshot(
            portfolio_id=portfolio.id,
            total_value=summary.total_value,
            known_value=summary.known_value,
            reporting_currency=portfolio.reporting_currency,
            quality_status=summary.quality.value,
            calculation_version=2,
            calculated_at=datetime.now(UTC),
        )
    )


def get_portfolio_summary(session: Session, portfolio: Portfolio) -> PortfolioSummaryRead:
    return _build_portfolio_summary(session, portfolio)


def _portfolio_read(portfolio: Portfolio) -> PortfolioRead:
    return PortfolioRead(
        id=str(portfolio.id),
        name=portfolio.name,
        reporting_currency=portfolio.reporting_currency,
        created_at=portfolio.created_at.isoformat(),
    )


def _build_portfolio_summary(session: Session, portfolio: Portfolio) -> PortfolioSummaryRead:
    sources = session.scalars(
        select(Source).where(Source.portfolio_id == portfolio.id).order_by(Source.created_at)
    ).all()
    source_by_id = {source.id: source for source in sources}
    source_ids = list(source_by_id)
    sync_warnings = latest_sync_warnings(session, source_ids)

    latest_snapshots: dict[UUID, WalletSnapshot] = {}
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
        for snapshot in snapshots:
            latest_snapshots[snapshot.source_id] = snapshot

    quantities: defaultdict[UUID, Decimal] = defaultdict(Decimal)
    holding_source_ids: defaultdict[UUID, set[UUID]] = defaultdict(set)
    now = datetime.now(UTC)
    stale_before = now - SOURCE_STALE_AFTER
    stale_price_before = now - PRICE_STALE_AFTER
    quality_by_source = {source.id: _source_quality(source, stale_before) for source in sources}
    stale_sources = any(
        source.retrieved_at and _as_utc(source.retrieved_at) < stale_before for source in sources
    )

    snapshot_ids = [snapshot.id for snapshot in latest_snapshots.values()]
    if snapshot_ids:
        balances = session.scalars(
            select(Balance).where(Balance.snapshot_id.in_(snapshot_ids))
        ).all()
        for balance in balances:
            quantities[balance.asset_id] += balance.quantity
            holding_source_ids[balance.asset_id].add(balance.source_id)

    transactions: list[Transaction] = []
    if source_ids:
        transactions = session.scalars(
            select(Transaction)
            .where(Transaction.source_id.in_(source_ids))
            .order_by(Transaction.occurred_at.desc(), Transaction.id.desc())
            .limit(12)
        ).all()

    asset_ids = list(quantities)
    activity_asset_ids = [
        asset_id
        for asset_id in dict.fromkeys(transaction.asset_id for transaction in transactions)
        if asset_id not in quantities
    ]
    asset_lookup_ids = [*asset_ids, *activity_asset_ids]
    assets = (
        session.scalars(select(Asset).where(Asset.id.in_(asset_lookup_ids))).all()
        if asset_lookup_ids
        else []
    )
    asset_by_id = {asset.id: asset for asset in assets}
    if asset_ids:
        ranked_prices = (
            select(
                Price.id.label("price_id"),
                func.row_number()
                .over(
                    partition_by=Price.asset_id,
                    order_by=(Price.retrieved_at.desc(), Price.id.desc()),
                )
                .label("price_rank"),
            )
            .where(
                Price.asset_id.in_(asset_ids),
                Price.quote_currency == portfolio.reporting_currency,
            )
            .subquery()
        )
        price_rows = session.scalars(
            select(Price)
            .join(ranked_prices, Price.id == ranked_prices.c.price_id)
            .where(ranked_prices.c.price_rank == 1)
        ).all()
    else:
        price_rows = []
    price_by_asset: dict[UUID, Price] = {}
    price_quality_by_asset: dict[UUID, QualityStatus] = {}
    for price in price_rows:
        if price.asset_id in price_by_asset:
            continue
        price_by_asset[price.asset_id] = price
        price_quality = _quality(price.quality_status)
        freshness_reference = price.provider_updated_at or price.retrieved_at
        if (
            price_quality in {QualityStatus.FRESH, QualityStatus.ESTIMATED}
            and _as_utc(freshness_reference) < stale_price_before
        ):
            price_quality = QualityStatus.DELAYED
        price_quality_by_asset[price.asset_id] = price_quality

    holdings: list[HoldingRead] = []
    allocation_values: dict[str, Decimal] = {}
    known_value = Decimal("0")
    missing_prices = False
    negative_balance = False
    stale_prices = False
    estimated_prices = False
    for asset_id, quantity in quantities.items():
        asset = asset_by_id.get(asset_id)
        if asset is None or quantity == 0:
            continue
        price = price_by_asset.get(asset_id)
        unit_price = price.price if price else None
        price_quality = price_quality_by_asset.get(asset_id, QualityStatus.FRESH)
        price_is_stale = price_quality == QualityStatus.DELAYED
        stale_prices = stale_prices or price_is_stale
        estimated_prices = estimated_prices or price_quality == QualityStatus.ESTIMATED
        value = (
            (quantity * unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if unit_price is not None and quantity > 0
            else None
        )
        position_sources = sorted(holding_source_ids[asset_id], key=str)
        position_source_names = [
            source_by_id[source_id].name
            for source_id in position_sources
            if source_id in source_by_id
        ]
        source_times = [
            source_by_id[source_id].retrieved_at
            for source_id in position_sources
            if source_id in source_by_id and source_by_id[source_id].retrieved_at
        ]
        if quantity < 0:
            negative_balance = True
        source_position_qualities = [quality_by_source[source_id] for source_id in position_sources]
        if unit_price is None:
            missing_prices = True
        if unit_price is None:
            position_quality = QualityStatus.UNMATCHED
        elif quantity < 0:
            position_quality = QualityStatus.NEEDS_REVIEW
        elif any(quality in INCOMPLETE_QUALITIES for quality in source_position_qualities):
            position_quality = next(
                quality for quality in source_position_qualities if quality in INCOMPLETE_QUALITIES
            )
        elif price_quality in INCOMPLETE_QUALITIES:
            position_quality = price_quality
        elif price_is_stale or QualityStatus.DELAYED in source_position_qualities:
            position_quality = QualityStatus.DELAYED
        elif (
            price_quality == QualityStatus.ESTIMATED
            or QualityStatus.ESTIMATED in source_position_qualities
        ):
            position_quality = QualityStatus.ESTIMATED
        else:
            position_quality = QualityStatus.FRESH
        if value is None:
            if unit_price is not None and quantity >= 0:
                missing_prices = True
        else:
            known_value += value
            allocation_values[str(asset_id)] = value
        holdings.append(
            HoldingRead(
                asset={
                    "id": asset.canonical_id,
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "network": asset.network_id,
                    "contractAddress": asset.contract_address,
                },
                quantity=quantity,
                unit_price=unit_price,
                value=value,
                source_ids=[str(source_id) for source_id in position_sources],
                provenance=HoldingProvenance(
                    balance_sources=position_source_names,
                    balance_retrieved_at=max(source_times) if source_times else None,
                    price_provider=price.provider if price else None,
                    price_retrieved_at=price.retrieved_at if price else None,
                    price_provider_updated_at=price.provider_updated_at if price else None,
                    quality=position_quality,
                ),
            )
        )

    percentages = allocation_percentages(allocation_values)
    allocation = [
        AllocationRead(
            name=asset_by_id[UUID(asset_id)].symbol,
            value=value,
            percentage=percentages.get(asset_id, Decimal("0")),
            color=ALLOCATION_COLORS[index % len(ALLOCATION_COLORS)],
        )
        for index, (asset_id, value) in enumerate(allocation_values.items())
    ]
    holdings.sort(key=lambda holding: holding.value or Decimal("-1"), reverse=True)

    has_balance_snapshot = any(
        source.kind in {"wallet", "exchange_balance_import"} and source.id in latest_snapshots
        for source in sources
    )
    incomplete_price_quality = any(
        quality in INCOMPLETE_QUALITIES for quality in price_quality_by_asset.values()
    )
    incomplete = (
        missing_prices
        or negative_balance
        or incomplete_price_quality
        or not has_balance_snapshot
        or any(source.kind == "exchange_import" for source in sources)
        or any(quality in INCOMPLETE_QUALITIES for quality in quality_by_source.values())
    )
    if incomplete:
        portfolio_quality = QualityStatus.PARTIAL
    elif stale_prices or QualityStatus.DELAYED in quality_by_source.values():
        portfolio_quality = QualityStatus.DELAYED
    elif estimated_prices or QualityStatus.ESTIMATED in quality_by_source.values():
        portfolio_quality = QualityStatus.ESTIMATED
    else:
        portfolio_quality = QualityStatus.FRESH
    total_value = None if incomplete else known_value

    source_reads = [
        SourceRead(
            id=str(source.id),
            name=source.name,
            kind=source.kind,
            network=source.network_id,
            address_label=_mask_address(source.public_address),
            last_updated_at=source.retrieved_at,
            quality=quality_by_source[source.id],
            coverage=(
                latest_snapshots[source.id].coverage if source.id in latest_snapshots else None
            ),
            warnings=(
                [
                    *(
                        latest_snapshots[source.id].warnings
                        if source.id in latest_snapshots
                        else []
                    ),
                    *([sync_warnings[source.id]] if source.id in sync_warnings else []),
                ]
            ),
        )
        for source in sources
    ]
    source_name = {source.id: source.name for source in sources}
    activity_ids = [transaction.id for transaction in transactions]
    activity_matches = (
        session.scalars(
            select(TransferMatch).where(
                (TransferMatch.outgoing_transaction_id.in_(activity_ids))
                | (TransferMatch.incoming_transaction_id.in_(activity_ids))
            )
        ).all()
        if activity_ids
        else []
    )
    transfer_status_by_transaction: dict[UUID, str] = {}
    for match in activity_matches:
        transfer_status_by_transaction[match.outgoing_transaction_id] = match.status
        transfer_status_by_transaction[match.incoming_transaction_id] = match.status
    activity = [
        ActivityRead(
            id=str(transaction.id),
            kind=_activity_kind(transaction.kind),
            asset_symbol=asset_by_id[transaction.asset_id].symbol
            if transaction.asset_id in asset_by_id
            else "Unknown",
            quantity=abs(transaction.quantity),
            source_name=source_name.get(transaction.source_id, "Unknown source"),
            occurred_at=transaction.occurred_at,
            status=(
                transaction.quality_status
                if transaction.quality_status in {"user_confirmed", "rejected"}
                else "confirmed"
                if _quality(transaction.quality_status) == QualityStatus.FRESH
                else "needs_review"
            ),
            transaction_hash=transaction.transaction_hash,
            external_record_id=transaction.external_record_id,
            quote_amount=transaction.quote_amount,
            quote_currency=transaction.quote_currency,
            transfer_status=transfer_status_by_transaction.get(transaction.id),
        )
        for transaction in transactions
    ]

    history_statement = select(ValuationSnapshot).where(
        ValuationSnapshot.portfolio_id == portfolio.id,
        ValuationSnapshot.reporting_currency == portfolio.reporting_currency,
        ValuationSnapshot.total_value.is_not(None),
    )
    first_import_at = (
        _as_utc(portfolio.import_history_started_at)
        if portfolio.import_history_started_at is not None
        else min(
            (_as_utc(source.created_at) for source in sources if source.kind == "exchange_import"),
            default=None,
        )
    )
    if first_import_at is not None:
        history_statement = history_statement.where(
            or_(
                ValuationSnapshot.calculated_at < first_import_at,
                ValuationSnapshot.calculation_version >= 2,
            )
        )
    history_rows = session.scalars(
        history_statement.order_by(ValuationSnapshot.calculated_at.desc()).limit(30)
    ).all()
    history_rows.reverse()
    history = [
        float(snapshot.total_value) for snapshot in history_rows if snapshot.total_value is not None
    ]
    change_24h: Decimal | None = None
    change_percent_24h: Decimal | None = None
    if total_value is not None:
        cutoff = datetime.now(UTC) - timedelta(hours=23)
        baseline = next(
            (
                snapshot
                for snapshot in reversed(history_rows)
                if _as_utc(snapshot.calculated_at) <= cutoff
            ),
            None,
        )
        if baseline and baseline.total_value is not None:
            change_24h = total_value - baseline.total_value
            if baseline.total_value != 0:
                change_percent_24h = (change_24h / baseline.total_value * 100).quantize(
                    Decimal("0.01")
                )

    return PortfolioSummaryRead(
        id=str(portfolio.id),
        name=portfolio.name,
        is_demo=False,
        reporting_currency=portfolio.reporting_currency,
        total_value=total_value,
        known_value=known_value,
        change_24h=change_24h,
        change_percent_24h=change_percent_24h,
        calculated_at=now.isoformat(),
        quality=portfolio_quality,
        warnings=_portfolio_warnings(
            sources,
            missing_prices=missing_prices,
            negative_balance=negative_balance,
            stale_sources=stale_sources,
            stale_prices=stale_prices,
            missing_balance_snapshot=not has_balance_snapshot,
        ),
        holdings=holdings,
        sources=source_reads,
        allocation=allocation,
        activity=activity,
        history=history,
    )


def _quality(value: str) -> QualityStatus:
    try:
        return QualityStatus(value)
    except ValueError:
        return QualityStatus.NEEDS_REVIEW


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def _source_quality(source: Source, stale_before: datetime) -> QualityStatus:
    quality = _quality(source.quality_status)
    if quality == QualityStatus.FRESH and source.retrieved_at:
        if _as_utc(source.retrieved_at) < stale_before:
            return QualityStatus.DELAYED
    return quality


def _portfolio_warnings(
    sources: list[Source],
    *,
    missing_prices: bool,
    negative_balance: bool,
    stale_sources: bool,
    stale_prices: bool,
    missing_balance_snapshot: bool,
) -> list[str]:
    warnings: list[str] = []
    if any(source.kind == "exchange_import" for source in sources):
        warnings.append(
            "Imported CSV rows are shown as activity and are not added to current wallet balances. "
            "The history may be incomplete or overlap connected wallet activity."
        )
    if missing_balance_snapshot:
        warnings.append(
            "No saved wallet or exchange-balance snapshot is available for current balances. "
            "Imported transaction history does not establish a current balance."
        )
    if missing_prices:
        warnings.append(
            "Some recognized assets have no available price; those values are not included."
        )
    if negative_balance:
        warnings.append(
            "At least one derived position is negative. Its value is withheld until the "
            "opening history is reviewed."
        )
    if stale_sources:
        warnings.append("Some wallet balances are older than 24 hours and may be delayed.")
    if stale_prices:
        warnings.append("Some asset prices are older than 10 minutes and may be delayed.")
    return warnings


def _mask_address(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= 12:
        return f"{value[:3]}…{value[-3:]}"
    return f"{value[:6]}…{value[-4:]}"


def _activity_kind(value: str) -> str:
    normalized = value.lower()
    if normalized in {"receive", "received", "deposit", "transfer_in"}:
        return "received" if normalized in {"receive", "received", "transfer_in"} else "deposit"
    if normalized in {"send", "sent", "withdrawal", "transfer_out"}:
        return "sent" if normalized in {"send", "sent", "transfer_out"} else "withdrawal"
    if normalized == "fee":
        return "fee"
    return "trade"
