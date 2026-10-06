import asyncio
from datetime import UTC, datetime
from decimal import Decimal

import httpx

from app.connectors.base import (
    BalanceConnector,
    NormalizedBalance,
    ProviderNotConfiguredError,
    ProviderRequestError,
)
from app.connectors.blockchain.networks import NetworkConfig
from app.connectors.rpc import json_rpc

SYMBOL_SELECTOR = "0x95d89b41"
DECIMALS_SELECTOR = "0x313ce567"
BALANCE_OF_SELECTOR = "0x70a08231"


def _decode_uint256(value: object) -> int:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ProviderRequestError("The EVM RPC returned invalid contract data.")
    try:
        return int(value, 16)
    except ValueError as exc:
        raise ProviderRequestError("The EVM RPC returned invalid contract data.") from exc


def _decode_symbol(value: object) -> str:
    if not isinstance(value, str) or not value.startswith("0x"):
        return ""
    try:
        raw = bytes.fromhex(value[2:])
    except ValueError:
        return ""

    # ERC-20 symbols are usually ABI strings; a few older tokens return bytes32.
    if len(raw) >= 64:
        offset = int.from_bytes(raw[:32], "big")
        if offset + 32 <= len(raw):
            length = int.from_bytes(raw[offset : offset + 32], "big")
            end = offset + 32 + length
            if end <= len(raw):
                raw = raw[offset + 32 : end]
    raw = raw.split(b"\x00", 1)[0]
    return raw.decode("utf-8", errors="replace").strip()[:24]


class EvmConnector(BalanceConnector):
    def __init__(self, network: NetworkConfig) -> None:
        self.network = network
        self.network_id = network.id

    async def get_balances(
        self, public_address: str, client: httpx.AsyncClient
    ) -> list[NormalizedBalance]:
        if not self.network.rpc_url or not self.network.chain_id:
            raise ProviderNotConfiguredError(f"{self.network.name} RPC is not configured.")

        actual_chain_id = await json_rpc(client, self.network.rpc_url, "eth_chainId", [])
        if _decode_uint256(actual_chain_id) != self.network.chain_id:
            raise ProviderRequestError(
                f"The configured RPC endpoint is not connected to {self.network.name}."
            )

        block_hex = await json_rpc(client, self.network.rpc_url, "eth_blockNumber", [])
        block_number = _decode_uint256(block_hex)
        block_tag = hex(block_number)
        native_balance, token_balances = await asyncio.gather(
            json_rpc(
                client,
                self.network.rpc_url,
                "eth_getBalance",
                [public_address, block_tag],
            ),
            self._read_tokens(client, public_address, block_tag),
        )
        retrieved_at = datetime.now(UTC)
        balances = [
            NormalizedBalance(
                asset_id=f"{self.network_id}:native",
                symbol=self.network.native_symbol,
                name=self.network.native_name,
                network_id=self.network_id,
                quantity=Decimal(_decode_uint256(native_balance)).scaleb(-18),
                contract_address=None,
                decimals=18,
                source_record_ids=(),
                retrieved_at=retrieved_at,
                block_reference=f"block:{block_number}",
            )
        ]
        balances.extend(
            NormalizedBalance(
                asset_id=f"{self.network_id}:{contract.lower()}",
                symbol=symbol or f"{contract[:6]}…{contract[-4:]}",
                name=symbol or "Unverified ERC-20 token",
                network_id=self.network_id,
                quantity=Decimal(amount).scaleb(-decimals),
                contract_address=contract,
                decimals=decimals,
                source_record_ids=(contract,),
                retrieved_at=retrieved_at,
                block_reference=f"block:{block_number}",
            )
            for contract, amount, decimals, symbol in token_balances
            if amount > 0
        )
        return balances

    async def _read_tokens(
        self,
        client: httpx.AsyncClient,
        public_address: str,
        block_tag: str,
    ) -> list[tuple[str, int, int, str]]:
        if not self.network.token_contracts:
            return []

        if not self.network.rpc_url:
            raise ProviderNotConfiguredError(f"{self.network.name} RPC is not configured.")

        padded_address = public_address[2:].lower().rjust(64, "0")

        async def read_token(contract: str) -> tuple[str, int, int, str]:
            balance_data, decimals_data = await asyncio.gather(
                json_rpc(
                    client,
                    self.network.rpc_url,
                    "eth_call",
                    [{"to": contract, "data": BALANCE_OF_SELECTOR + padded_address}, block_tag],
                ),
                json_rpc(
                    client,
                    self.network.rpc_url,
                    "eth_call",
                    [{"to": contract, "data": DECIMALS_SELECTOR}, block_tag],
                ),
            )
            amount = _decode_uint256(balance_data)
            decimals = _decode_uint256(decimals_data)
            if decimals > 255:
                raise ProviderRequestError("An EVM token returned invalid decimal metadata.")
            try:
                symbol_data = await json_rpc(
                    client,
                    self.network.rpc_url,
                    "eth_call",
                    [{"to": contract, "data": SYMBOL_SELECTOR}, block_tag],
                )
            except ProviderRequestError:
                symbol_data = ""
            symbol = _decode_symbol(symbol_data)
            return contract, amount, decimals, symbol

        results = await asyncio.gather(
            *(read_token(contract) for contract in self.network.token_contracts)
        )
        return results
