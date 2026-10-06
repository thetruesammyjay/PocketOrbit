from collections.abc import Mapping


def identify_asset(record: Mapping[str, str], known_assets: list[dict[str, str]]) -> dict[str, str] | None:
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
            if asset.get("network_id") == network and asset.get("contract_address", "").lower() == contract.lower():
                return asset
    return None
