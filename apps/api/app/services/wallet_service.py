from datetime import UTC, datetime
from decimal import Decimal

import httpx

from app.connectors.base import (
    BalanceConnector,
    NormalizedBalance,
    ProviderNotConfiguredError,
)
from app.connectors.blockchain.evm import MAX_DISCOVERED_ERC20, EvmConnector
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

BALANCE_STORAGE_SCALE = 18
BALANCE_STORAGE_WHOLE_DIGITS = 20


def _fits_balance_storage(quantity: Decimal) -> bool:
    """Return whether Numeric(38, 18) can store a quantity without rounding."""
    if not quantity.is_finite():
        return False
    if quantity == 0:
        return True
    if quantity.copy_abs().adjusted() + 1 > BALANCE_STORAGE_WHOLE_DIGITS:
        return False

    _, digits, exponent = quantity.as_tuple()
    significant_digits = list(digits)
    while (
        exponent < -BALANCE_STORAGE_SCALE
        and significant_digits
        and significant_digits[-1] == 0
    ):
        significant_digits.pop()
        exponent += 1
    return exponent >= -BALANCE_STORAGE_SCALE


def wallet_capabilities() -> dict[str, object]:
    networks = supported_networks()
    persistence_configured = bool((settings.database_url or "").strip())
    configured_networks = []
    for network in networks.values():
        network_info: dict[str, object] = {
            "id": network.id,
            "name": network.name,
            "configured": bool(network.rpc_url and network.rpc_url.strip()),
            "coverage": (
                "SOL and SPL / Token-2022 fungible tokens"
                if network.id == "solana"
                else (
                    "native coin and indexed ERC-20 tokens when Alchemy or a compatible provider "
                    "supports it; otherwise configured contracts"
                    if settings.evm_token_discovery.strip().lower() != "configured_only"
                    else "native coin and configured ERC-20 contracts"
                )
            ),
        }
        if network.id != "solana":
            network_info["tokenDiscoveryMode"] = settings.evm_token_discovery
            network_info["automaticTokenDiscovery"] = (
                settings.evm_token_discovery.strip().lower() != "configured_only"
            )
            network_info["dedicatedIndexedProviderConfigured"] = bool(network.indexed_rpc_url)
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
        "persistence": persistence_configured,
        "message": (
            "Wallet reads use public addresses only. Authenticated wallet sources and snapshots "
            "are saved to the account; signing access is never requested."
            if persistence_configured
            else (
                "Wallet preview reads are not saved because database persistence is not "
                "configured. Signing access is never requested."
            )
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
    connector = _connector(network)
    async with httpx.AsyncClient(timeout=timeout) as client:
        balances = await connector.get_balances(public_address, client)
        persistable_balances: list[NormalizedBalance] = []
        omitted_unpersistable_balances = 0
        for balance in balances:
            if _fits_balance_storage(balance.quantity):
                persistable_balances.append(balance)
            else:
                omitted_unpersistable_balances += 1
        balances = persistable_balances
        prices = await resolve_prices(balances, network, quote_currency, client)

    retrieved_at = max((balance.retrieved_at for balance in balances), default=datetime.now(UTC))
    warnings = list(prices.warnings)
    if network.id != "solana":
        if isinstance(connector, EvmConnector) and connector.uses_indexed_rpc_fallback:
            warnings.append(
                "The configured chain RPC did not respond to its chain check; the configured "
                "indexed RPC endpoint was used for chain reads."
            )
        if (
            isinstance(connector, EvmConnector)
            and connector.uses_alchemy_portfolio_chain_fallback
        ):
            warnings.append(
                "The configured chain RPCs were unavailable; native and ERC-20 balances came "
                "from the Alchemy Portfolio API."
            )
        indexed_discovery = (
            isinstance(connector, EvmConnector) and connector.uses_indexed_token_discovery
        )
        if indexed_discovery:
            discovery_source = (
                "Alchemy Portfolio API"
                if connector.uses_alchemy_portfolio_api
                else "the configured indexed RPC provider"
            )
            warnings.append(
                f"ERC-20 balances were discovered by {discovery_source}. "
                "NFTs and DeFi positions are not included."
            )
            warnings.append(
                "Alchemy Portfolio API balances are not pinned to an EVM block reference."
                if connector.uses_alchemy_portfolio_chain_fallback
                else (
                    "Indexed ERC-20 balances use the provider's latest state and are not pinned "
                    "to the native balance's block reference."
                )
            )
            if connector.indexed_token_failures:
                warnings.append(
                    f"{connector.indexed_token_failures} indexed token balance(s) could not be "
                    "read or normalized; the snapshot is partial."
                )
            if connector.indexed_provider_partial_errors:
                warnings.append(
                    f"The indexed provider reported {connector.indexed_provider_partial_errors} "
                    "partial network result(s); some balances may be missing."
                )
            if connector.indexed_token_discovery_truncated:
                warnings.append(
                    "Token discovery reached its maximum page limit; later pages were not read "
                    "and the snapshot is partial."
                )
            if connector.indexed_token_limit_reached:
                warnings.append(
                    f"Token discovery reached the {MAX_DISCOVERED_ERC20} positive-token limit; "
                    f"{connector.indexed_token_limit_skipped} additional positive balance(s) "
                    "from that page were omitted and later pages were not read. The snapshot is "
                    "partial."
                )
        else:
            warnings.append(
                "This snapshot includes the native coin and only explicitly configured ERC-20 "
                "contracts because indexed token discovery is unavailable."
            )
        if network.invalid_token_contract_entries:
            warnings.append(
                f"{network.invalid_token_contract_entries} invalid configured EVM token "
                "contract address(es) were ignored."
            )
        if network.token_contracts_truncated:
            warnings.append("Only the first 30 unique configured EVM token contracts were read.")
    else:
        warnings.append(
            "This snapshot covers fungible token balances. NFTs and DeFi positions "
            "are not included."
        )
    if omitted_unpersistable_balances:
        warnings.append(
            f"{omitted_unpersistable_balances} balance(s) exceeded the stored quantity precision "
            "and were omitted so their amounts would not be rounded. The snapshot is partial."
        )
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
                decimals=balance.decimals,
                quote_currency=quote_currency,
                unit_price=quote.amount if quote else None,
                value=value,
                quality=_balance_quality(quote),
                balance_provenance=BalanceProvenance(
                    source_name=(
                        f"Alchemy Portfolio API ({network.name})"
                        if isinstance(connector, EvmConnector)
                        and connector.uses_alchemy_portfolio_api
                        and (
                            balance.contract_address is not None
                            or connector.uses_alchemy_portfolio_chain_fallback
                        )
                        else (
                            f"Indexed RPC fallback ({network.name})"
                            if isinstance(connector, EvmConnector)
                            and connector.uses_indexed_rpc_fallback
                            else f"Configured {network.name} RPC"
                        )
                    ),
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
            f"No recognized price was returned for {missing_prices} asset(s); those values "
            "are omitted from the known value."
        )

    indexed_discovery_incomplete = isinstance(connector, EvmConnector) and (
        not connector.uses_indexed_token_discovery
        or connector.indexed_token_failures > 0
        or connector.indexed_provider_partial_errors > 0
        or connector.indexed_token_discovery_truncated
        or connector.indexed_token_limit_reached
    )
    coverage_limited = omitted_unpersistable_balances > 0 or (
        network.id != "solana" and indexed_discovery_incomplete
    )
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
            else (
                "native_and_indexed_erc20_balances"
                if isinstance(connector, EvmConnector) and connector.uses_indexed_token_discovery
                else "native_and_configured_erc20_balances"
            )
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
