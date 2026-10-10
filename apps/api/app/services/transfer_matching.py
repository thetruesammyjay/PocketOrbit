from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Transaction
from app.models.asset import Asset
from app.models.portfolio import Portfolio
from app.models.source import Source
from app.models.transfer_match import TransferMatch
from app.schemas.imports import TransferMatchRead

OUTGOING_KINDS = {"send", "sent", "withdrawal", "transfer_out"}
INCOMING_KINDS = {"receive", "received", "deposit", "transfer_in"}
REVIEWED = "user_confirmed"


def refresh_transfer_suggestions(session: Session, portfolio: Portfolio) -> None:
    sources = session.scalars(select(Source).where(Source.portfolio_id == portfolio.id)).all()
    source_by_id = {source.id: source for source in sources}
    transactions = (
        session.scalars(
            select(Transaction)
            .where(Transaction.source_id.in_(source_by_id), Transaction.quality_status == REVIEWED)
            .order_by(Transaction.occurred_at, Transaction.id)
        ).all()
        if source_by_id
        else []
    )
    active_matches = session.scalars(
        select(TransferMatch).where(
            TransferMatch.portfolio_id == portfolio.id,
            TransferMatch.status.in_(["suggested", "matched"]),
        )
    ).all()
    used_outgoing = {match.outgoing_transaction_id for match in active_matches}
    used_incoming = {match.incoming_transaction_id for match in active_matches}
    assets = (
        session.scalars(
            select(Asset).where(
                Asset.id.in_({transaction.asset_id for transaction in transactions})
            )
        ).all()
        if transactions
        else []
    )
    asset_by_id = {asset.id: asset for asset in assets}
    outgoing = [
        transaction
        for transaction in transactions
        if transaction.kind in OUTGOING_KINDS
        and transaction.quantity < 0
        and transaction.id not in used_outgoing
    ]
    incoming = [
        transaction
        for transaction in transactions
        if transaction.kind in INCOMING_KINDS
        and transaction.quantity > 0
        and transaction.id not in used_incoming
    ]

    candidates: list[tuple[Decimal, Transaction, Transaction, str]] = []
    for sent in outgoing:
        sent_source = source_by_id.get(sent.source_id)
        sent_asset = asset_by_id.get(sent.asset_id)
        if not sent_source or not sent_asset:
            continue
        for received in incoming:
            received_source = source_by_id.get(received.source_id)
            if (
                received.asset_id != sent.asset_id
                or not received_source
                or received.source_id == sent.source_id
                or received_source.name.casefold() == sent_source.name.casefold()
            ):
                continue
            sent_time = _as_utc(sent.occurred_at)
            received_time = _as_utc(received.occurred_at)
            elapsed = abs(received_time - sent_time)
            same_hash = bool(
                sent.transaction_hash
                and received.transaction_hash
                and sent.transaction_hash.casefold() == received.transaction_hash.casefold()
            )
            if elapsed > (timedelta(hours=36) if same_hash else timedelta(hours=2)):
                continue
            sent_quantity = abs(sent.quantity)
            if sent.fee_quantity and sent.fee_asset_id == sent.asset_id:
                sent_quantity = max(Decimal("0"), sent_quantity - sent.fee_quantity)
            received_quantity = abs(received.quantity)
            if sent_quantity == 0 or received_quantity == 0:
                continue
            difference = abs(sent_quantity - received_quantity) / max(
                sent_quantity, received_quantity
            )
            if same_hash:
                if difference > Decimal("0.01"):
                    continue
                confidence = Decimal("0.99")
                rationale = (
                    "The records have the same transaction hash and exact network asset. "
                    "Review the amounts before confirming."
                )
            else:
                if difference > Decimal("0.001"):
                    continue
                confidence = (
                    Decimal("0.90")
                    if difference == 0 and elapsed <= timedelta(minutes=20)
                    else Decimal("0.80")
                )
                rationale = (
                    "The exact network asset, near-equal amount, and close timestamps make "
                    "this a candidate. Confirm it only if both records are your own transfer."
                )
            candidates.append((confidence - difference, sent, received, rationale))

    candidates_by_outgoing: dict[UUID, list[tuple[Decimal, Transaction, Transaction, str]]] = {}
    candidates_by_incoming: dict[UUID, list[tuple[Decimal, Transaction, Transaction, str]]] = {}
    for candidate in candidates:
        _, sent, received, _ = candidate
        candidates_by_outgoing.setdefault(sent.id, []).append(candidate)
        candidates_by_incoming.setdefault(received.id, []).append(candidate)

    best_for_outgoing = _unique_best_candidates(candidates_by_outgoing)
    best_for_incoming = _unique_best_candidates(candidates_by_incoming)

    for score, sent, received, rationale in best_for_outgoing.values():
        incoming_best = best_for_incoming.get(received.id)
        if incoming_best is None or incoming_best[1].id != sent.id:
            continue
        existing = session.scalar(
            select(TransferMatch.id).where(
                TransferMatch.outgoing_transaction_id == sent.id,
                TransferMatch.incoming_transaction_id == received.id,
            )
        )
        if existing:
            continue
        session.add(
            TransferMatch(
                portfolio_id=portfolio.id,
                outgoing_transaction_id=sent.id,
                incoming_transaction_id=received.id,
                status="suggested",
                confidence=max(Decimal("0"), min(Decimal("1"), score)),
                rationale=rationale,
            )
        )


def _unique_best_candidates(
    candidates_by_transaction: dict[UUID, list[tuple[Decimal, Transaction, Transaction, str]]],
) -> dict[UUID, tuple[Decimal, Transaction, Transaction, str]]:
    best: dict[UUID, tuple[Decimal, Transaction, Transaction, str]] = {}
    for transaction_id, candidates in candidates_by_transaction.items():
        highest_score = max(candidate[0] for candidate in candidates)
        highest_scoring = [candidate for candidate in candidates if candidate[0] == highest_score]
        if len(highest_scoring) == 1:
            best[transaction_id] = highest_scoring[0]
    return best


def list_transfer_matches(session: Session, portfolio: Portfolio) -> list[TransferMatchRead]:
    matches = session.scalars(
        select(TransferMatch)
        .where(TransferMatch.portfolio_id == portfolio.id)
        .order_by(TransferMatch.created_at.desc())
        .limit(200)
    ).all()
    transactions = (
        session.scalars(
            select(Transaction).where(
                Transaction.id.in_(
                    {
                        transaction_id
                        for match in matches
                        for transaction_id in (
                            match.outgoing_transaction_id,
                            match.incoming_transaction_id,
                        )
                    }
                )
            )
        ).all()
        if matches
        else []
    )
    transaction_by_id = {transaction.id: transaction for transaction in transactions}
    source_ids = {transaction.source_id for transaction in transactions}
    sources = (
        session.scalars(select(Source).where(Source.id.in_(source_ids))).all() if source_ids else []
    )
    source_by_id = {source.id: source for source in sources}
    asset_ids = {transaction.asset_id for transaction in transactions}
    assets = (
        session.scalars(select(Asset).where(Asset.id.in_(asset_ids))).all() if asset_ids else []
    )
    asset_by_id = {asset.id: asset for asset in assets}

    result: list[TransferMatchRead] = []
    for match in matches:
        sent = transaction_by_id.get(match.outgoing_transaction_id)
        received = transaction_by_id.get(match.incoming_transaction_id)
        if not sent or not received:
            continue
        asset = asset_by_id.get(sent.asset_id)
        result.append(
            TransferMatchRead(
                id=str(match.id),
                outgoing_transaction_id=str(sent.id),
                incoming_transaction_id=str(received.id),
                asset_symbol=asset.symbol if asset else "Unknown",
                quantity_sent=str(abs(sent.quantity)),
                quantity_received=str(abs(received.quantity)),
                outgoing_source=source_by_id[sent.source_id].name,
                incoming_source=source_by_id[received.source_id].name,
                occurred_at=_as_utc(sent.occurred_at),
                confidence=float(match.confidence),
                rationale=match.rationale,
                status=match.status,
            )
        )
    return result


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
