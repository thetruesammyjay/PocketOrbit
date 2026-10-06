from app.services.wallet_service import refresh_public_wallet


async def sync_wallet(network_id: str, public_address: str) -> list[dict[str, str]]:
    return await refresh_public_wallet(network_id, public_address)
