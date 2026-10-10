from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Transaction
from app.models.asset import Asset
from app.models.balance import Balance
from app.models.import_job import ImportJob
from app.models.portfolio import Portfolio
from app.models.price import Price
from app.models.source import Source
from app.models.transfer_match import TransferMatch
from app.models.wallet_snapshot import WalletSnapshot
from app.schemas.imports import (
    PerformanceCoverageRead,
    PerformanceLotRead,
    PerformanceRead,
    RealizedPnlRead,
)

INBOUND = {
    "buy",
    "purchase",
    "deposit",
    "receive",
    "received",
    "reward",
    "staking",
    "transfer_in",
    "swap_in",
}
OUTBOUND = {"sell", "sale", "withdrawal", "send", "sent", "transfer_out", "swap_out"}
DISPOSALS_WITH_PROCEEDS = {"sell", "sale", "swap_out"}
TRANSFER_IN = {"receive", "received", "deposit", "transfer_in"}
CENT = Decimal("0.01")


@dataclass
class Lot:
    quantity: Decimal
    basis: Decimal | None
    source_name: str


def get_portfolio_performance(session: Session, portfolio: Portfolio) -> PerformanceRead:
    reasons: list[str] = []
    sources = session.scalars(
        select(Source).where(Source.portfolio_id == portfolio.id).order_by(Source.name)
    ).all()
    source_by_id = {source.id: source for source in sources}
    exchange_sources = [source for source in sources if source.kind == "exchange_import"]
    source_ids = [source.id for source in exchange_sources]
    jobs = (
        session.scalars(
            select(ImportJob)
            .where(ImportJob.portfolio_id == portfolio.id, ImportJob.source_id.in_(source_ids))
            .order_by(ImportJob.created_at)
        ).all()
        if source_ids
        else []
    )
    jobs_by_source: defaultdict[UUID, list[ImportJob]] = defaultdict(list)
    for job in jobs:
        if job.source_id:
            jobs_by_source[job.source_id].append(job)

    coverage: list[PerformanceCoverageRead] = []
    for source in exchange_sources:
        source_jobs = jobs_by_source[source.id]
        asserted = any(job.history_complete for job in source_jobs)
        start_values = [job.coverage_start_at for job in source_jobs if job.coverage_start_at]
        end_values = [job.coverage_end_at for job in source_jobs if job.coverage_end_at]
        rejected = sum(job.rows_rejected for job in source_jobs)
        coverage.append(
            PerformanceCoverageRead(
                source_name=source.name,
                start_at=min(start_values, key=_as_utc) if start_values else None,
                end_at=max(end_values, key=_as_utc) if end_values else None,
                complete_history_asserted=asserted,
                rows_imported=sum(job.rows_accepted for job in source_jobs),
                rows_rejected=rejected,
            )
        )
        if not asserted:
            reasons.append(
                f"{source.name}: no import is marked as the account's full available history."
            )
        if rejected:
            reasons.append(
                f"{source.name}: {rejected} CSV row(s) were rejected; "
                "remove or correct the incomplete import."
            )

    if any(source.kind == "wallet" for source in sources):
        reasons.append(
            "Public wallet balances do not yet include transaction history. "
            "Portfolio wide performance is incomplete."
        )
    all_transactions = (
        session.scalars(
            select(Transaction)
            .where(Transaction.source_id.in_(source_ids))
            .order_by(Transaction.occurred_at, Transaction.id)
        ).all()
        if source_ids
        else []
    )
    if not all_transactions:
        reasons.append("Import transaction history before calculating performance.")

    user_rejected = [
        transaction for transaction in all_transactions if transaction.quality_status == "rejected"
    ]
    if user_rejected:
        reasons.append(
            f"{len(user_rejected)} imported record(s) were rejected during review; "
            "the history needs correction."
        )
    unreviewed = [
        transaction
        for transaction in all_transactions
        if transaction.quality_status not in {"user_confirmed", "rejected"}
    ]
    if unreviewed:
        reasons.append(
            f"Review {len(unreviewed)} imported transaction record(s) "
            "before using performance figures."
        )

    unresolved_transfers = session.scalar(
        select(TransferMatch.id)
        .where(
            TransferMatch.portfolio_id == portfolio.id,
            TransferMatch.status == "suggested",
        )
        .limit(1)
    )
    if unresolved_transfers:
        reasons.append("Review suggested internal transfers before calculating performance.")
    confirmed_transfer_rows = session.scalars(
        select(TransferMatch).where(
            TransferMatch.portfolio_id == portfolio.id,
            TransferMatch.status == "matched",
        )
    ).all()
    transfer_transaction_ids = {
        transaction_id
        for match in confirmed_transfer_rows
        for transaction_id in (match.outgoing_transaction_id, match.incoming_transaction_id)
    }

    asset_ids = {transaction.asset_id for transaction in all_transactions}
    assets = (
        session.scalars(select(Asset).where(Asset.id.in_(asset_ids))).all() if asset_ids else []
    )
    asset_by_id = {asset.id: asset for asset in assets}
    for asset in assets:
        if asset.canonical_id.startswith("import:"):
            reasons.append(
                f"{asset.symbol}: ticker-only identity is unresolved, "
                "so records cannot be safely combined."
            )

    lots_by_asset: defaultdict[UUID, list[Lot]] = defaultdict(list)
    realized_events: list[RealizedPnlRead] = []
    known_realized = Decimal("0")
    has_realized_value = False
    for transaction in all_transactions:
        if (
            transaction.id in transfer_transaction_ids
            or transaction.quality_status != "user_confirmed"
        ):
            continue
        asset = asset_by_id.get(transaction.asset_id)
        source = source_by_id.get(transaction.source_id)
        if not asset or not source:
            reasons.append("An imported transaction refers to a missing asset or source record.")
            continue
        kind = transaction.kind.lower()
        quantity = abs(transaction.quantity)
        if quantity == 0:
            reasons.append(
                f"{asset.symbol}: a zero quantity record cannot be included in FIFO calculation."
            )
            continue
        if transaction.fee_quantity and transaction.fee_quantity > 0:
            reasons.append(
                f"{asset.symbol}: transaction fees need a supported fee valuation "
                "before performance is complete."
            )

        if kind in INBOUND:
            basis: Decimal | None = None
            if kind in {"buy", "purchase", "swap_in"}:
                if (
                    transaction.quote_amount is not None
                    and transaction.quote_currency == portfolio.reporting_currency
                    and not transaction.fee_quantity
                ):
                    basis = transaction.quote_amount
                elif (
                    transaction.quote_amount is not None
                    and transaction.quote_currency != portfolio.reporting_currency
                ):
                    reasons.append(
                        f"{asset.symbol}: {transaction.quote_currency} acquisition "
                        "values need historical currency conversion."
                    )
                else:
                    reasons.append(
                        f"{asset.symbol}: {kind} record has no acquisition value "
                        f"in {portfolio.reporting_currency}."
                    )
            elif kind in TRANSFER_IN:
                reasons.append(
                    f"{asset.symbol}: unmatched incoming activity has unknown opening cost basis."
                )
            else:
                reasons.append(
                    f"{asset.symbol}: reward or staking basis is not established "
                    "by imported activity."
                )
            lots_by_asset[asset.id].append(
                Lot(quantity=quantity, basis=basis, source_name=source.name)
            )
            continue

        if kind in OUTBOUND:
            remaining = quantity
            consumed_basis = Decimal("0")
            basis_known = True
            asset_lots = lots_by_asset[asset.id]
            while remaining > 0 and asset_lots:
                lot = asset_lots[0]
                used = min(remaining, lot.quantity)
                if lot.basis is None:
                    basis_known = False
                elif lot.quantity > 0:
                    consumed_basis += lot.basis * (used / lot.quantity)
                    lot.basis -= lot.basis * (used / lot.quantity)
                lot.quantity -= used
                remaining -= used
                if lot.quantity == 0:
                    asset_lots.pop(0)
            if remaining > 0:
                basis_known = False
                reasons.append(
                    f"{asset.symbol}: outbound quantity exceeds reviewed FIFO lots by {remaining}."
                )
            if kind in DISPOSALS_WITH_PROCEEDS:
                proceeds: Decimal | None = None
                if (
                    transaction.quote_amount is not None
                    and transaction.quote_currency == portfolio.reporting_currency
                ):
                    proceeds = transaction.quote_amount
                elif (
                    transaction.quote_currency
                    and transaction.quote_currency != portfolio.reporting_currency
                ):
                    reasons.append(
                        f"{asset.symbol}: {transaction.quote_currency} sale proceeds "
                        "need historical currency conversion."
                    )
                else:
                    reasons.append(
                        f"{asset.symbol}: sale record has no proceeds "
                        f"in {portfolio.reporting_currency}."
                    )
                pnl = proceeds - consumed_basis if proceeds is not None and basis_known else None
                if pnl is not None:
                    known_realized += pnl
                    has_realized_value = True
                else:
                    reasons.append(f"{asset.symbol}: FIFO basis for this disposal is incomplete.")
                realized_events.append(
                    RealizedPnlRead(
                        transaction_id=str(transaction.id),
                        asset_symbol=asset.symbol,
                        source_name=source.name,
                        quantity=quantity,
                        proceeds=proceeds,
                        cost_basis=consumed_basis if basis_known else None,
                        pnl=pnl,
                    )
                )
            else:
                reasons.append(
                    f"{asset.symbol}: outgoing activity may have left the tracked portfolio; "
                    "proceeds are not known."
                )
            continue

        reasons.append(
            f"{asset.symbol}: transaction type '{kind}' is not supported by FIFO performance."
        )

    positions: list[PerformanceLotRead] = []
    known_unrealized = Decimal("0")
    has_unrealized_value = False
    latest_prices = _latest_prices(session, asset_ids, portfolio.reporting_currency)
    for asset_id, asset_lots in lots_by_asset.items():
        open_lots = [lot for lot in asset_lots if lot.quantity > 0]
        quantity = sum((lot.quantity for lot in open_lots), Decimal("0"))
        if quantity <= 0:
            continue
        asset = asset_by_id.get(asset_id)
        if not asset:
            continue
        basis_known = all(lot.basis is not None for lot in open_lots)
        basis = (
            sum((lot.basis or Decimal("0") for lot in open_lots), Decimal("0"))
            if basis_known
            else None
        )
        price = latest_prices.get(asset_id)
        market_value = (
            (quantity * price.price).quantize(CENT, rounding=ROUND_HALF_UP) if price else None
        )
        pnl = market_value - basis if market_value is not None and basis is not None else None
        if pnl is not None:
            known_unrealized += pnl
            has_unrealized_value = True
        if not basis_known:
            reasons.append(f"{asset.symbol}: at least one open lot has unknown acquisition basis.")
        if price is None:
            reasons.append(
                f"{asset.symbol}: no current {portfolio.reporting_currency} price "
                "is available for open lots."
            )
        elif _as_utc(price.retrieved_at) < datetime.now(UTC) - timedelta(minutes=10):
            reasons.append(f"{asset.symbol}: the latest price is older than 10 minutes.")
        positions.append(
            PerformanceLotRead(
                asset_symbol=asset.symbol,
                quantity=quantity,
                cost_basis=basis,
                market_value=market_value,
                pnl=pnl,
                source_names=sorted({lot.source_name for lot in open_lots}),
            )
        )

    _check_balance_coverage(session, portfolio, sources, source_ids, all_transactions, reasons)
    reasons = list(dict.fromkeys(reasons))
    status = "complete" if not reasons else ("partial" if all_transactions else "unavailable")
    realized = (
        _money(known_realized)
        if has_realized_value
        or not any(tx.kind in DISPOSALS_WITH_PROCEEDS for tx in all_transactions)
        else None
    )
    unrealized = _money(known_unrealized) if has_unrealized_value or not positions else None
    total = (
        _money((realized or Decimal("0")) + (unrealized or Decimal("0")))
        if status == "complete"
        else None
    )
    return PerformanceRead(
        status=status,
        currency=portfolio.reporting_currency,
        realized_pnl=realized,
        unrealized_pnl=unrealized,
        total_pnl=total,
        open_positions=positions,
        realized_events=realized_events,
        coverage=coverage,
        reasons=reasons,
        calculated_at=datetime.now(UTC),
    )


def _latest_prices(session: Session, asset_ids: set[UUID], currency: str) -> dict[UUID, Price]:
    if not asset_ids:
        return {}
    prices = session.scalars(
        select(Price)
        .where(Price.asset_id.in_(asset_ids), Price.quote_currency == currency)
        .order_by(Price.retrieved_at.desc(), Price.id.desc())
    ).all()
    result: dict[UUID, Price] = {}
    for price in prices:
        result.setdefault(price.asset_id, price)
    return result


def _check_balance_coverage(
    session: Session,
    portfolio: Portfolio,
    sources: list[Source],
    transaction_source_ids: list[UUID],
    transactions: list[Transaction],
    reasons: list[str],
) -> None:
    balance_sources = [source for source in sources if source.kind == "exchange_balance_import"]
    if not balance_sources:
        return
    source_by_name = {
        source.name.casefold(): source for source in sources if source.id in transaction_source_ids
    }
    for balance_source in balance_sources:
        matching_source = source_by_name.get(balance_source.name.casefold())
        if matching_source is None:
            reasons.append(
                f"{balance_source.name}: current balances have no matching "
                "imported activity history."
            )
            continue
        snapshot = session.scalar(
            select(WalletSnapshot)
            .where(WalletSnapshot.source_id == balance_source.id)
            .order_by(WalletSnapshot.retrieved_at.desc(), WalletSnapshot.id.desc())
            .limit(1)
        )
        if snapshot is None:
            reasons.append(f"{balance_source.name}: no current balance snapshot is available.")
            continue
        balances = session.scalars(select(Balance).where(Balance.snapshot_id == snapshot.id)).all()
        balance_by_asset: defaultdict[UUID, Decimal] = defaultdict(Decimal)
        for balance in balances:
            balance_by_asset[balance.asset_id] += balance.quantity
        source_transactions = [
            tx
            for tx in transactions
            if tx.source_id == matching_source.id and tx.quality_status == "user_confirmed"
        ]
        ledger_by_asset: defaultdict[UUID, Decimal] = defaultdict(Decimal)
        for transaction in source_transactions:
            ledger_by_asset[transaction.asset_id] += transaction.quantity
        if set(balance_by_asset) != set(ledger_by_asset) or any(
            abs(balance_by_asset[asset_id] - ledger_by_asset.get(asset_id, Decimal("0")))
            > Decimal("0.00000001")
            for asset_id in set(balance_by_asset) | set(ledger_by_asset)
        ):
            reasons.append(
                f"{balance_source.name}: reviewed imported history does not reconcile "
                "to the latest balance statement."
            )


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
