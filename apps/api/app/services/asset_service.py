from collections.abc import Mapping
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.asset import Asset


def get_or_create_asset(
    session: Session,
    *,
    canonical_id: str,
    symbol: str,
    name: str,
    network_id: str | None,
    contract_address: str | None,
    decimals: int,
    refresh_metadata: bool = False,
) -> Asset:
    values = {
        "id": uuid4(),
        "canonical_id": canonical_id,
        "symbol": symbol,
        "name": name,
        "network_id": network_id,
        "contract_address": contract_address,
        "decimals": decimals,
    }
    with session.no_autoflush:
        asset = session.scalar(select(Asset).where(Asset.canonical_id == canonical_id))
    if asset is not None:
        if refresh_metadata:
            asset.symbol = symbol
            asset.name = name
        return asset

    dialect_name = session.get_bind().dialect.name
    if dialect_name == "postgresql":
        statement = postgresql_insert(Asset).values(**values)
        statement = statement.on_conflict_do_nothing(index_elements=[Asset.canonical_id])
    elif dialect_name == "sqlite":
        statement = sqlite_insert(Asset).values(**values)
        statement = statement.on_conflict_do_nothing(index_elements=[Asset.canonical_id])
    else:
        try:
            with session.begin_nested():
                session.add(Asset(**values))
                session.flush()
        except IntegrityError:
            with session.no_autoflush:
                asset = session.scalar(select(Asset).where(Asset.canonical_id == canonical_id))
            if asset is None:
                raise
        else:
            with session.no_autoflush:
                asset = session.scalar(select(Asset).where(Asset.canonical_id == canonical_id))
            if asset is None:
                raise RuntimeError("The asset insert did not produce a readable asset record.")
        if refresh_metadata:
            asset.symbol = symbol
            asset.name = name
        return asset

    # Assets are shared across portfolios, so concurrent imports and wallet syncs can race
    # between the lookup and insert. ON CONFLICT keeps the request idempotent on our DBs.
    with session.no_autoflush:
        session.execute(statement)
        asset = session.scalar(select(Asset).where(Asset.canonical_id == canonical_id))
    if asset is None:
        raise RuntimeError("The asset insert did not produce a readable asset record.")
    if refresh_metadata:
        asset.symbol = symbol
        asset.name = name
    return asset


def identify_asset(
    record: Mapping[str, str], known_assets: list[dict[str, str]]
) -> dict[str, str] | None:
    """Match by canonical/provider identity or network+contract, never ticker alone."""
    provider_id = record.get("provider_asset_id")
    if provider_id:
        for asset in known_assets:
            if asset.get("provider_asset_id") == provider_id:
                return asset

    network = record.get("network_id")
    contract = record.get("contract_address")
    if network and contract:
        for asset in known_assets:
            if (
                asset.get("network_id") == network
                and asset.get("contract_address", "").lower() == contract.lower()
            ):
                return asset
    return None
