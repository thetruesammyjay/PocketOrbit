from datetime import UTC, datetime
from decimal import Decimal

import httpx

from app.connectors.base import (
    BalanceConnector,
    ProviderNotConfiguredError,
    ProviderRequestError,
)
from app.connectors.blockchain.evm import EvmConnector
from app.connectors.blockchain.networks import NetworkConfig, supported_networks
from app.connectors.blockchain.solana import SolanaConnector
from app.core.config import settings
from app.schemas.common import QualityStatus
from app.schemas.wallet import (
    BalanceProvenance,
    LiveWalletBalance,
    PriceProvenance,
    WalletSyncResponse,
)
from app.services.pricing_service import PriceQuote, resolve_prices


def wallet_capabilities() -> dict[str, object]:
    networks = supported_networks()
    configured_networks = []
    for network in networks.values():
        network_info: dict[str, object] = {
            "id": network.id,
            "name": network.name,
            "configured": bool(network.rpc_url and network.rpc_url.strip()),
            "coverage": (
                "SOL and SPL / Token-2022 fungible tokens"
                if network.id == "solana"
                else "native coin and configured ERC-20 contracts"
            ),
        }
        if network.id != "solana":
            network_info["configuredTokenContracts"] = len(network.token_contracts)
            network_info["invalidTokenContractEntries"] = network.invalid_token_contract_entries
            network_info["tokenContractsTruncated"] = network.token_contracts_truncated
        configured_networks.append(network_info)
    return {
        "priceProvider": {
            "name": "CoinGecko",
            "configured": bool((settings.coingecko_api_key or "").strip()),
        },
        "networks": configured_networks,
        "persistence": False,
        "message": (
            "Wallet reads use public addresses only. The API does not save wallet addresses "
            "or request signing access."
        ),
    }


def _connector(network: NetworkConfig) -> BalanceConnector:
    if network.id == "solana":
        return SolanaConnector(network.rpc_url)
    return EvmConnector(network)


def _balance_quality(quote: PriceQuote | None) -> QualityStatus:
    if not quote:
        return QualityStatus.UNMATCHED
    return quote.quality


async def refresh_public_wallet(
    network_id: str,
    public_address: str,
    quote_currency: str = "USD",
) -> WalletSyncResponse:
    """Fetch a read-only wallet snapshot. The result is not persisted."""
    network = supported_networks().get(network_id)
    if not network:
        raise ValueError("Choose a supported network.")
    if not network.rpc_url or not network.rpc_url.strip():
        raise ProviderNotConfiguredError(f"{network.name} RPC is not configured.")

    timeout = httpx.Timeout(15.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        balances = await _connector(network).get_balances(public_address, client)
        prices = await resolve_prices(balances, network, quote_currency, client)

    retrieved_at = max((balance.retrieved_at for balance in balances), default=datetime.now(UTC))
    warnings = list(prices.warnings)
    if network.id != "solana":
        warnings.append(
            "EVM JSON-RPC does not enumerate arbitrary ERC-20 tokens. This snapshot includes "
            "the native coin and only token contracts configured for this network."
        )
        if network.invalid_token_contract_entries:
            warnings.append(
                f"{network.invalid_token_contract_entries} invalid configured EVM token contract address(es) were ignored."
            )
        if network.token_contracts_truncated:
            warnings.append("Only the first 30 unique configured EVM token contracts were read.")
    else:
        warnings.append("This snapshot covers fungible token balances. NFTs and DeFi positions are not included.")
    live_balances: list[LiveWalletBalance] = []
    known_value = Decimal("0")
    missing_prices = 0
    delayed_prices = False
    estimated_prices = False
    for balance in balances:
        quote = prices.quotes.get(balance.asset_id)
        value = balance.quantity * quote.amount if quote else None
        if value is None:
            missing_prices += 1
        else:
            known_value += value
        if quote and quote.quality == QualityStatus.DELAYED:
            delayed_prices = True
        if quote and quote.quality == QualityStatus.ESTIMATED:
            estimated_prices = True
        live_balances.append(
            LiveWalletBalance(
                asset_id=balance.asset_id,
                symbol=balance.symbol,
                name=balance.name,
                network=balance.network_id,
                contract_address=balance.contract_address,
                quantity=balance.quantity,
                quote_currency=quote_currency,
                unit_price=quote.amount if quote else None,
                value=value,
                quality=_balance_quality(quote),
                balance_provenance=BalanceProvenance(
                    source_name=f"Configured {network.name} RPC",
                    source_record_ids=list(balance.source_record_ids),
                    retrieved_at=balance.retrieved_at,
                    block_reference=balance.block_reference,
                ),
                price_provenance=(
                    PriceProvenance(
                        source_name=quote.source_name,
                        retrieved_at=quote.retrieved_at,
                        provider_updated_at=quote.provider_updated_at,
                        quality=quote.quality,
                    )
                    if quote
                    else None
                ),
            )
        )

    if missing_prices:
        warnings.append(
            f"No recognized price was returned for {missing_prices} asset(s); those values are omitted from the known value."
        )

    coverage_limited = network.id != "solana"
    is_complete = not coverage_limited and missing_prices == 0
    if not is_complete:
        quality = QualityStatus.PARTIAL
    elif delayed_prices:
        quality = QualityStatus.DELAYED
    elif estimated_prices:
        quality = QualityStatus.ESTIMATED
    else:
        quality = QualityStatus.FRESH
    return WalletSyncResponse(
        network=network.id,
        network_name=network.name,
        coverage=(
            "native_and_spl_token2022_fungible_balances"
            if network.id == "solana"
            else "native_and_configured_erc20_balances"
        ),
        address=public_address,
        retrieved_at=retrieved_at,
        quote_currency=quote_currency,
        total_value=known_value if is_complete else None,
        known_value=known_value,
        quality=quality,
        balances=live_balances,
        warnings=list(dict.fromkeys(warnings)),
    )
