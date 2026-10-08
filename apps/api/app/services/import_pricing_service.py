from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.connectors.base import NormalizedBalance
from app.connectors.blockchain.networks import supported_networks
from app.connectors.market_data.base import MarketPriceBatch
from app.models.activity import Transaction
from app.models.asset import Asset
from app.models.balance import Balance
from app.models.portfolio import Portfolio
from app.models.price import Price
from app.models.wallet_snapshot import WalletSnapshot
from app.services.persistent_portfolios import record_valuation_snapshot
from app.services.pricing_service import resolve_prices

MAX_PRICED_IMPORT_ASSETS = 200
NATIVE_ASSET_IDS = {
    ("solana", "solana"),
    ("ethereum", "ethereum:native"),
    ("base", "base:native"),
    ("arbitrum", "arbitrum:native"),
}


async def price_imported_assets(
    session: Session, portfolio: Portfolio, source_id: UUID
) -> list[str]:
    """Attach current market quotes to assets with unambiguous network identities."""
    asset_ids = set(
        session.scalars(
            select(Transaction.asset_id).where(Transaction.source_id == source_id).distinct()
        ).all()
    )
    balance_snapshot = session.scalar(
        select(WalletSnapshot)
        .where(WalletSnapshot.source_id == source_id)
        .order_by(WalletSnapshot.retrieved_at.desc(), WalletSnapshot.id.desc())
        .limit(1)
    )
    balance_rows = (
        session.scalars(
            select(Balance).where(Balance.snapshot_id == balance_snapshot.id)
        ).all()
        if balance_snapshot
        else []
    )
    asset_ids.update(balance.asset_id for balance in balance_rows)
    if not asset_ids:
        return []

    assets = session.scalars(select(Asset).where(Asset.id.in_(asset_ids))).all()
    networks = supported_networks()
    balances_by_network: dict[str, list[NormalizedBalance]] = {}
    skipped = 0
    retrieved_at = datetime.now(UTC)
    for asset in assets:
        network_id = asset.network_id
        network = networks.get(network_id or "")
        is_known_native = (network_id or "", asset.canonical_id) in NATIVE_ASSET_IDS
        if not network or (not asset.contract_address and not is_known_native):
            skipped += 1
            continue
        balances_by_network.setdefault(network.id, []).append(
            NormalizedBalance(
                asset_id=asset.canonical_id,
                symbol=asset.symbol,
                name=asset.name,
                network_id=network.id,
                quantity=Decimal("1"),
                contract_address=asset.contract_address,
                decimals=asset.decimals,
                source_record_ids=(),
                retrieved_at=retrieved_at,
            )
        )

    eligible_count = sum(len(items) for items in balances_by_network.values())
    limited = eligible_count > MAX_PRICED_IMPORT_ASSETS
    remaining = MAX_PRICED_IMPORT_ASSETS
    for network_id in list(balances_by_network):
        if remaining <= 0:
            del balances_by_network[network_id]
            continue
        balances_by_network[network_id] = balances_by_network[network_id][:remaining]
        remaining -= len(balances_by_network[network_id])

    timeout = httpx.Timeout(15.0, connect=5.0)
    warnings: list[str] = []
    async with httpx.AsyncClient(timeout=timeout) as client:
        for network_id, balances in balances_by_network.items():
            network = networks[network_id]
            batch: MarketPriceBatch = await resolve_prices(
                balances, network, portfolio.reporting_currency, client
            )
            warnings.extend(batch.warnings)
            by_canonical_id = {asset.canonical_id: asset for asset in assets}
            for canonical_id, quote in batch.quotes.items():
                asset = by_canonical_id.get(canonical_id)
                if asset is None:
                    continue
                session.add(
                    Price(
                        asset_id=asset.id,
                        provider=quote.source_name[:64],
                        quote_currency=portfolio.reporting_currency,
                        price=quote.amount,
                        provider_updated_at=quote.provider_updated_at,
                        quality_status=quote.quality.value,
                        retrieved_at=quote.retrieved_at,
                    )
                )

    if skipped:
        warnings.append(
            f"Prices were not requested for {skipped} asset(s) without a supported, "
            "exact network identity."
        )
    if limited:
        warnings.append(
            f"Price lookup was limited to the first {MAX_PRICED_IMPORT_ASSETS} "
            "identified assets in this import."
        )
    session.flush()
    if balance_snapshot:
        price_rows = session.scalars(
            select(Price).where(
                Price.asset_id.in_({balance.asset_id for balance in balance_rows}),
                Price.quote_currency == portfolio.reporting_currency,
            )
        ).all()
        latest_price_by_asset: dict[UUID, Price] = {}
        for price in price_rows:
            current = latest_price_by_asset.get(price.asset_id)
            if current is None or price.retrieved_at > current.retrieved_at:
                latest_price_by_asset[price.asset_id] = price
        balance_snapshot.known_value = sum(
            (
                (balance.quantity * latest_price_by_asset[balance.asset_id].price).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                for balance in balance_rows
                if balance.asset_id in latest_price_by_asset
            ),
            start=Decimal("0"),
        )
    record_valuation_snapshot(session, portfolio)
    session.commit()
    return list(dict.fromkeys(warnings))
