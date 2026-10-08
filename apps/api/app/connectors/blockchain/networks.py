from dataclasses import dataclass
from urllib.parse import quote

from app.core.config import settings


@dataclass(frozen=True)
class NetworkConfig:
    id: str
    name: str
    native_symbol: str
    native_name: str
    native_price_id: str
    price_platform_id: str
    rpc_url: str | None
    chain_id: int | None = None
    alchemy_network_slug: str | None = None
    indexed_rpc_url: str | None = None
    token_contracts: tuple[str, ...] = ()
    invalid_token_contract_entries: int = 0
    token_contracts_truncated: bool = False


def _contract_config(value: str) -> dict[str, object]:
    entries = [contract.strip() for contract in value.split(",") if contract.strip()]
    valid = [
        contract
        for contract in entries
        if len(contract) == 42
        and contract.startswith("0x")
        and all(character in "0123456789abcdefABCDEF" for character in contract[2:])
    ]
    unique = list(dict.fromkeys(contract.lower() for contract in valid))
    return {
        "token_contracts": tuple(unique[:30]),
        "invalid_token_contract_entries": len(entries) - len(valid),
        "token_contracts_truncated": len(unique) > 30,
    }


def _alchemy_rpc_url(network_slug: str) -> str | None:
    api_key = (settings.alchemy_api_key or "").strip()
    return f"https://{network_slug}.g.alchemy.com/v2/{quote(api_key, safe='')}" if api_key else None


def supported_networks() -> dict[str, NetworkConfig]:
    ethereum_indexer = settings.ethereum_indexed_rpc_url or _alchemy_rpc_url("eth-mainnet")
    base_indexer = settings.base_indexed_rpc_url or _alchemy_rpc_url("base-mainnet")
    arbitrum_indexer = settings.arbitrum_indexed_rpc_url or _alchemy_rpc_url("arb-mainnet")
    return {
        "solana": NetworkConfig(
            id="solana",
            name="Solana",
            native_symbol="SOL",
            native_name="Solana",
            native_price_id="solana",
            price_platform_id="solana",
            rpc_url=settings.solana_rpc_url,
        ),
        "ethereum": NetworkConfig(
            id="ethereum",
            name="Ethereum",
            native_symbol="ETH",
            native_name="Ether",
            native_price_id="ethereum",
            price_platform_id="ethereum",
            rpc_url=settings.ethereum_rpc_url or settings.evm_rpc_url or ethereum_indexer,
            chain_id=1,
            alchemy_network_slug="eth-mainnet",
            indexed_rpc_url=ethereum_indexer,
            **_contract_config(settings.ethereum_token_contracts),
        ),
        "base": NetworkConfig(
            id="base",
            name="Base",
            native_symbol="ETH",
            native_name="Ether",
            native_price_id="ethereum",
            price_platform_id="base",
            rpc_url=settings.base_rpc_url or base_indexer,
            chain_id=8453,
            alchemy_network_slug="base-mainnet",
            indexed_rpc_url=base_indexer,
            **_contract_config(settings.base_token_contracts),
        ),
        "arbitrum": NetworkConfig(
            id="arbitrum",
            name="Arbitrum One",
            native_symbol="ETH",
            native_name="Ether",
            native_price_id="ethereum",
            price_platform_id="arbitrum-one",
            rpc_url=settings.arbitrum_rpc_url or arbitrum_indexer,
            chain_id=42161,
            alchemy_network_slug="arb-mainnet",
            indexed_rpc_url=arbitrum_indexer,
            **_contract_config(settings.arbitrum_token_contracts),
        ),
    }
