from sqlalchemy.orm import Session

from app.models.balance import Balance
from app.models.portfolio import Portfolio
from app.models.price import Price
from app.models.source import Source
from app.models.wallet_snapshot import WalletSnapshot
from app.schemas.wallet import WalletSyncResponse
from app.services.asset_service import get_or_create_asset
from app.services.persistent_portfolios import record_valuation_snapshot


def save_wallet_snapshot(
    session: Session,
    portfolio: Portfolio,
    source: Source,
    result: WalletSyncResponse,
) -> WalletSnapshot:
    snapshot = WalletSnapshot(
        source_id=source.id,
        retrieved_at=result.retrieved_at,
        quote_currency=result.quote_currency,
        known_value=result.known_value,
        total_value=result.total_value,
        quality_status=result.quality.value,
        coverage=result.coverage,
        warnings=result.warnings,
    )
    session.add(snapshot)
    session.flush()

    for balance in result.balances:
        contract_address = (
            balance.contract_address
            if balance.network == "solana" or not balance.contract_address
            else balance.contract_address.lower()
        )
        canonical_id = (
            f"{balance.network}:{contract_address}" if contract_address else balance.asset_id
        )
        asset = get_or_create_asset(
            session,
            canonical_id=canonical_id,
            symbol=balance.symbol,
            name=balance.name,
            network_id=balance.network,
            contract_address=contract_address,
            decimals=balance.decimals,
            refresh_metadata=True,
        )

        session.add(
            Balance(
                source_id=source.id,
                snapshot_id=snapshot.id,
                asset_id=asset.id,
                quantity=balance.quantity,
                quality_status=balance.quality.value,
                source_record_id=",".join(balance.balance_provenance.source_record_ids)[:256]
                or None,
                retrieved_at=balance.balance_provenance.retrieved_at,
            )
        )
        if balance.unit_price is not None and balance.price_provenance:
            session.add(
                Price(
                    asset_id=asset.id,
                    provider=balance.price_provenance.source_name[:64],
                    quote_currency=balance.quote_currency,
                    price=balance.unit_price,
                    provider_updated_at=balance.price_provenance.provider_updated_at,
                    quality_status=balance.price_provenance.quality.value,
                    retrieved_at=balance.price_provenance.retrieved_at,
                )
            )

    source.quality_status = result.quality.value
    source.retrieved_at = result.retrieved_at
    session.flush()
    record_valuation_snapshot(session, portfolio)
    return snapshot
