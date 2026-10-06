from dataclasses import dataclass

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


def supported_networks() -> dict[str, NetworkConfig]:
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
            rpc_url=settings.ethereum_rpc_url or settings.evm_rpc_url,
            chain_id=1,
            **_contract_config(settings.ethereum_token_contracts),
        ),
        "base": NetworkConfig(
            id="base",
            name="Base",
            native_symbol="ETH",
            native_name="Ether",
            native_price_id="ethereum",
            price_platform_id="base",
            rpc_url=settings.base_rpc_url,
            chain_id=8453,
            **_contract_config(settings.base_token_contracts),
        ),
        "arbitrum": NetworkConfig(
            id="arbitrum",
            name="Arbitrum One",
            native_symbol="ETH",
            native_name="Ether",
            native_price_id="ethereum",
            price_platform_id="arbitrum-one",
            rpc_url=settings.arbitrum_rpc_url,
            chain_id=42161,
            **_contract_config(settings.arbitrum_token_contracts),
        ),
    }
