import asyncio
import re
from datetime import UTC, datetime
from urllib.parse import quote

import httpx

from app.connectors.base import (
    BalanceConnector,
    NormalizedBalance,
    ProviderNotConfiguredError,
    ProviderRequestError,
    decimal_from_base_units,
)
from app.connectors.blockchain.networks import NetworkConfig
from app.connectors.rpc import json_rpc
from app.core.config import settings

SYMBOL_SELECTOR = "0x95d89b41"
DECIMALS_SELECTOR = "0x313ce567"
BALANCE_OF_SELECTOR = "0x70a08231"
EVM_ADDRESS_PATTERN = re.compile(r"^0x[0-9a-fA-F]{40}$")
MAX_DISCOVERED_ERC20 = 200
INDEXER_PAGE_SIZE = 100
INDEXER_MAX_PAGES = 10
MAX_CONCURRENT_TOKEN_READS = 8


def _decode_uint256(value: object) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"0x[0-9a-fA-F]+", value):
        raise ProviderRequestError("The EVM RPC returned invalid contract data.")
    try:
        decoded = int(value, 16)
    except ValueError as exc:
        raise ProviderRequestError("The EVM RPC returned invalid contract data.") from exc
    if decoded > 2**256 - 1:
        raise ProviderRequestError("The EVM RPC returned invalid contract data.")
    return decoded


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
        self.rpc_url = network.rpc_url
        self.uses_indexed_rpc_fallback = False
        self.uses_alchemy_portfolio_api = False
        self.uses_alchemy_portfolio_chain_fallback = False
        self.uses_indexed_token_discovery = False
        self.indexed_token_failures = 0
        self.indexed_provider_partial_errors = 0
        self.indexed_token_discovery_truncated = False
        self.indexed_token_limit_reached = False
        self.indexed_token_limit_skipped = 0

    async def get_balances(
        self, public_address: str, client: httpx.AsyncClient
    ) -> list[NormalizedBalance]:
        if not self.rpc_url or not self.network.chain_id:
            raise ProviderNotConfiguredError(f"{self.network.name} RPC is not configured.")

        indexed_discovery_enabled = (
            settings.evm_token_discovery.strip().lower() != "configured_only"
        )
        try:
            actual_chain_id = await json_rpc(client, self.rpc_url, "eth_chainId", [])
        except ProviderRequestError as configured_rpc_error:
            indexed_rpc_url = self.network.indexed_rpc_url
            fallback_error = configured_rpc_error
            actual_chain_id = None
            if (
                indexed_discovery_enabled
                and indexed_rpc_url
                and indexed_rpc_url != self.rpc_url
            ):
                try:
                    actual_chain_id = await json_rpc(client, indexed_rpc_url, "eth_chainId", [])
                except ProviderRequestError as indexed_rpc_error:
                    fallback_error = indexed_rpc_error
                else:
                    self.rpc_url = indexed_rpc_url
                    self.uses_indexed_rpc_fallback = True

            if actual_chain_id is None:
                if indexed_discovery_enabled:
                    try:
                        portfolio_balances = await self._read_alchemy_portfolio_api_balances(
                            client,
                            public_address,
                        )
                    except ProviderRequestError as portfolio_error:
                        raise ProviderRequestError(
                            f"The configured {self.network.name} RPC and indexed RPC fallback "
                            f"failed: {fallback_error} The Alchemy Portfolio API fallback failed: "
                            f"{portfolio_error}"
                        ) from None
                    if portfolio_balances is not None:
                        self.uses_indexed_token_discovery = True
                        self.uses_alchemy_portfolio_api = True
                        self.uses_alchemy_portfolio_chain_fallback = True
                        return portfolio_balances
                    raise ProviderRequestError(
                        f"The configured {self.network.name} RPC and indexed RPC fallback could "
                        f"not be used: {fallback_error} No usable Alchemy Portfolio API fallback "
                        "is configured."
                    ) from None
                raise ProviderRequestError(
                    f"The configured {self.network.name} RPC could not be used: {fallback_error}"
                ) from None
        if _decode_uint256(actual_chain_id) != self.network.chain_id:
            raise ProviderRequestError(f"The RPC endpoint is not connected to {self.network.name}.")

        block_hex = await json_rpc(client, self.rpc_url, "eth_blockNumber", [])
        block_number = _decode_uint256(block_hex)
        block_tag = hex(block_number)
        native_balance, token_balances = await asyncio.gather(
            json_rpc(
                client,
                self.rpc_url,
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
                quantity=decimal_from_base_units(_decode_uint256(native_balance), 18),
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
                name=name or "Unverified ERC-20 token",
                network_id=self.network_id,
                quantity=decimal_from_base_units(amount, decimals),
                contract_address=contract,
                decimals=decimals,
                source_record_ids=(contract,),
                retrieved_at=retrieved_at,
                block_reference=(
                    None if self.uses_indexed_token_discovery else f"block:{block_number}"
                ),
            )
            for contract, amount, decimals, symbol, name in token_balances
            if amount > 0
        )
        return balances

    async def _read_tokens(
        self,
        client: httpx.AsyncClient,
        public_address: str,
        block_tag: str,
    ) -> list[tuple[str, int, int, str, str]]:
        discovery_mode = settings.evm_token_discovery.strip().lower()
        if discovery_mode != "configured_only":
            discovered = await self._read_indexed_tokens(client, public_address)
            if discovered is not None:
                self.uses_indexed_token_discovery = True
                return discovered
            portfolio_tokens = await self._read_alchemy_portfolio_api_assets(
                client,
                public_address,
                include_native=False,
            )
            if portfolio_tokens is not None:
                self.uses_indexed_token_discovery = True
                self.uses_alchemy_portfolio_api = True
                return [
                    (contract, amount, decimals, symbol, name)
                    for contract, amount, decimals, symbol, name in portfolio_tokens
                    if contract is not None
                ]
            if discovery_mode == "alchemy":
                raise ProviderRequestError(
                    "The configured EVM provider does not support indexed ERC-20 discovery."
                )

        if not self.network.token_contracts:
            return []

        if not self.rpc_url:
            raise ProviderNotConfiguredError(f"{self.network.name} RPC is not configured.")

        padded_address = public_address[2:].lower().rjust(64, "0")

        semaphore = asyncio.Semaphore(MAX_CONCURRENT_TOKEN_READS)

        async def read_token(contract: str) -> tuple[str, int, int, str, str]:
            async with semaphore:
                return await _read_token(contract)

        async def _read_token(contract: str) -> tuple[str, int, int, str, str]:
            balance_data, decimals_data = await asyncio.gather(
                json_rpc(
                    client,
                    self.rpc_url,
                    "eth_call",
                    [{"to": contract, "data": BALANCE_OF_SELECTOR + padded_address}, block_tag],
                ),
                json_rpc(
                    client,
                    self.rpc_url,
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
                    self.rpc_url,
                    "eth_call",
                    [{"to": contract, "data": SYMBOL_SELECTOR}, block_tag],
                )
            except ProviderRequestError:
                symbol_data = ""
            symbol = _decode_symbol(symbol_data)
            return contract, amount, decimals, symbol, symbol

        results = await asyncio.gather(
            *(read_token(contract) for contract in self.network.token_contracts)
        )
        return results

    async def _read_alchemy_portfolio_api_balances(
        self,
        client: httpx.AsyncClient,
        public_address: str,
    ) -> list[NormalizedBalance] | None:
        assets = await self._read_alchemy_portfolio_api_assets(
            client,
            public_address,
            include_native=True,
        )
        if assets is None:
            return None

        retrieved_at = datetime.now(UTC)
        balances: list[NormalizedBalance] = []
        for contract, amount, decimals, symbol, name in assets:
            is_native = contract is None
            balances.append(
                NormalizedBalance(
                    asset_id=(
                        f"{self.network_id}:native"
                        if is_native
                        else f"{self.network_id}:{contract.lower()}"
                    ),
                    symbol=(
                        self.network.native_symbol
                        if is_native
                        else symbol or f"{contract[:6]}...{contract[-4:]}"
                    ),
                    name=(
                        self.network.native_name
                        if is_native
                        else name or "Unverified ERC-20 token"
                    ),
                    network_id=self.network_id,
                    quantity=decimal_from_base_units(amount, decimals),
                    contract_address=contract,
                    decimals=decimals,
                    source_record_ids=() if is_native else (contract,),
                    retrieved_at=retrieved_at,
                    block_reference=None,
                )
            )
        return balances

    async def _read_alchemy_portfolio_api_assets(
        self,
        client: httpx.AsyncClient,
        public_address: str,
        *,
        include_native: bool,
    ) -> list[tuple[str | None, int, int, str, str]] | None:
        api_key = (settings.alchemy_api_key or "").strip()
        network_slug = self.network.alchemy_network_slug
        if not api_key or not network_slug:
            return None

        endpoint = (
            "https://api.g.alchemy.com/data/v1/"
            f"{quote(api_key, safe='')}/assets/tokens/by-address"
        )
        token_candidates: dict[str, tuple[str, int, dict[str, object]]] = {}
        native_balance: tuple[str | None, int, int, str, str] | None = None
        page_key: str | None = None
        for _ in range(INDEXER_MAX_PAGES):
            request_body: dict[str, object] = {
                "addresses": [
                    {"address": public_address, "networks": [network_slug]},
                ],
                "withMetadata": True,
                "withPrices": False,
                "includeNativeTokens": include_native,
                "includeErc20Tokens": True,
                "includeBlockMetadata": False,
            }
            if page_key:
                request_body["pageKey"] = page_key
            try:
                response = await client.post(endpoint, json=request_body)
            except httpx.TimeoutException:
                raise ProviderRequestError("The Alchemy Portfolio API timed out.") from None
            except httpx.HTTPError:
                raise ProviderRequestError(
                    "The Alchemy Portfolio API could not be reached."
                ) from None

            if response.status_code in {403, 404, 405, 501}:
                if token_candidates or native_balance:
                    self.indexed_token_discovery_truncated = True
                    break
                return None
            if response.status_code == 429:
                raise ProviderRequestError("The Alchemy Portfolio API rate-limited this request.")
            if response.is_error:
                raise ProviderRequestError(
                    f"The Alchemy Portfolio API returned HTTP {response.status_code}."
                )
            try:
                payload = response.json()
            except ValueError:
                raise ProviderRequestError(
                    "The Alchemy Portfolio API returned invalid JSON."
                ) from None
            if not isinstance(payload, dict):
                raise ProviderRequestError(
                    "The Alchemy Portfolio API returned an invalid response."
                )
            data = payload.get("data")
            if not isinstance(data, dict) or not isinstance(data.get("tokens"), list):
                raise ProviderRequestError(
                    "The Alchemy Portfolio API returned an invalid token list."
                )

            provider_error = payload.get("error")
            if provider_error is not None:
                if not isinstance(provider_error, dict):
                    raise ProviderRequestError("The Alchemy Portfolio API reported an error.")
                partial_errors = provider_error.get("partialErrors")
                if not isinstance(partial_errors, list):
                    raise ProviderRequestError("The Alchemy Portfolio API reported an error.")
                network_failed = False
                for item in partial_errors:
                    if not isinstance(item, dict) or not isinstance(item.get("network"), str):
                        raise ProviderRequestError(
                            "The Alchemy Portfolio API returned malformed partial-error data."
                        )
                    if item["network"] == network_slug:
                        network_failed = True
                if network_failed:
                    self.indexed_provider_partial_errors += 1

            limit_reached_on_page = False
            for item in data["tokens"]:
                if not isinstance(item, dict):
                    raise ProviderRequestError(
                        "The Alchemy Portfolio API returned a malformed token entry."
                    )
                if item.get("error"):
                    self.indexed_token_failures += 1
                    continue
                if item.get("network") != network_slug:
                    raise ProviderRequestError(
                        "The Alchemy Portfolio API returned a token for an unexpected network."
                    )
                item_address = item.get("address")
                if (
                    not isinstance(item_address, str)
                    or item_address.lower() != public_address.lower()
                ):
                    raise ProviderRequestError(
                        "The Alchemy Portfolio API returned a token for an unexpected address."
                    )
                try:
                    amount = _decode_uint256(item.get("tokenBalance"))
                except ProviderRequestError:
                    self.indexed_token_failures += 1
                    continue
                if amount <= 0:
                    continue

                contract = item.get("tokenAddress")
                metadata = item.get("tokenMetadata")
                metadata = metadata if isinstance(metadata, dict) else {}
                if "tokenAddress" not in item:
                    raise ProviderRequestError(
                        "The Alchemy Portfolio API returned a token without a contract field."
                    )
                if contract is None:
                    if include_native:
                        native_balance = (
                            None,
                            amount,
                            18,
                            self.network.native_symbol,
                            self.network.native_name,
                        )
                    continue
                if not isinstance(contract, str) or not EVM_ADDRESS_PATTERN.fullmatch(contract):
                    raise ProviderRequestError(
                        "The Alchemy Portfolio API returned an invalid token contract."
                    )
                contract_key = contract.lower()
                if (
                    contract_key not in token_candidates
                    and len(token_candidates) >= MAX_DISCOVERED_ERC20
                ):
                    self.indexed_token_limit_reached = True
                    self.indexed_token_limit_skipped += 1
                    limit_reached_on_page = True
                    continue
                token_candidates[contract_key] = (contract, amount, metadata)

            next_page = data.get("pageKey")
            page_key = next_page if isinstance(next_page, str) and next_page else None
            if limit_reached_on_page:
                break
            if page_key is None:
                break
        else:
            self.indexed_token_discovery_truncated = True

        assets: list[tuple[str | None, int, int, str, str]] = []
        if native_balance:
            assets.append(native_balance)
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_TOKEN_READS)

        async def normalize_token(
            candidate: tuple[str, int, dict[str, object]],
        ) -> tuple[str, int, int, str, str] | None:
            contract, amount, metadata = candidate
            decimals = metadata.get("decimals")
            if (
                isinstance(decimals, bool)
                or not isinstance(decimals, int)
                or not 0 <= decimals <= 255
            ):
                if not self.rpc_url:
                    self.indexed_token_failures += 1
                    return None
                try:
                    async with semaphore:
                        decimals_data = await json_rpc(
                            client,
                            self.rpc_url,
                            "eth_call",
                            [{"to": contract, "data": DECIMALS_SELECTOR}, "latest"],
                        )
                    decimals = _decode_uint256(decimals_data)
                except ProviderRequestError:
                    self.indexed_token_failures += 1
                    return None
                if decimals > 255:
                    self.indexed_token_failures += 1
                    return None

            symbol = metadata.get("symbol")
            symbol = symbol.strip()[:24] if isinstance(symbol, str) else ""
            name = metadata.get("name")
            name = name.strip()[:160] if isinstance(name, str) else ""
            return contract, amount, decimals, symbol, name

        normalized_tokens = await asyncio.gather(
            *(normalize_token(candidate) for candidate in token_candidates.values())
        )
        assets.extend(token for token in normalized_tokens if token is not None)
        return assets

    async def _read_indexed_tokens(
        self, client: httpx.AsyncClient, public_address: str
    ) -> list[tuple[str, int, int, str, str]] | None:
        """Use Alchemy's optional token indexer, bounded to 200 current assets."""
        indexer_rpc_url = self.network.indexed_rpc_url or self.network.rpc_url
        if not indexer_rpc_url:
            raise ProviderNotConfiguredError(f"{self.network.name} RPC is not configured.")
        if indexer_rpc_url != self.rpc_url and self.network.chain_id is not None:
            indexer_chain_id = await json_rpc(client, indexer_rpc_url, "eth_chainId", [])
            if _decode_uint256(indexer_chain_id) != self.network.chain_id:
                raise ProviderRequestError(
                    f"The indexed RPC endpoint is not connected to {self.network.name}."
                )

        token_amounts: dict[str, int] = {}
        page_key: str | None = None
        for _ in range(INDEXER_MAX_PAGES):
            options: dict[str, object] = {"maxCount": INDEXER_PAGE_SIZE}
            if page_key:
                options["pageKey"] = page_key
            payload = await json_rpc(
                client,
                indexer_rpc_url,
                "alchemy_getTokenBalances",
                [public_address, "erc20", options],
                allow_unsupported_method=True,
            )
            if payload is None:
                return None
            if not isinstance(payload, dict) or not isinstance(payload.get("tokenBalances"), list):
                raise ProviderRequestError(
                    "The EVM token indexer returned an invalid balance list."
                )

            limit_reached_on_page = False
            for item in payload["tokenBalances"]:
                if not isinstance(item, dict):
                    raise ProviderRequestError(
                        "The EVM token indexer returned a malformed token entry."
                    )
                if item.get("error"):
                    self.indexed_token_failures += 1
                    continue
                contract = item.get("contractAddress")
                amount_value = item.get("tokenBalance")
                if not isinstance(contract, str) or not EVM_ADDRESS_PATTERN.fullmatch(contract):
                    raise ProviderRequestError(
                        "The EVM token indexer returned an invalid contract address."
                    )
                try:
                    amount = _decode_uint256(amount_value)
                except ProviderRequestError:
                    self.indexed_token_failures += 1
                    continue
                if amount > 0:
                    contract_key = contract.lower()
                    if contract_key in token_amounts:
                        token_amounts[contract_key] = amount
                    elif len(token_amounts) < MAX_DISCOVERED_ERC20:
                        token_amounts[contract_key] = amount
                    else:
                        # Keep the read bounded and stop pagination once omitted positive
                        # balances prove that the snapshot cannot be complete.
                        self.indexed_token_limit_reached = True
                        self.indexed_token_limit_skipped += 1
                        limit_reached_on_page = True

            next_page = payload.get("pageKey")
            page_key = next_page if isinstance(next_page, str) and next_page else None
            if limit_reached_on_page:
                break
            if page_key is None:
                break
        else:
            self.indexed_token_discovery_truncated = True

        semaphore = asyncio.Semaphore(MAX_CONCURRENT_TOKEN_READS)

        async def read_metadata(contract: str) -> tuple[str, int, int, str, str] | None:
            async with semaphore:
                try:
                    return await _read_metadata(contract)
                except ProviderRequestError:
                    self.indexed_token_failures += 1
                    return None

        async def _read_metadata(contract: str) -> tuple[str, int, int, str, str]:
            metadata = await json_rpc(
                client,
                indexer_rpc_url,
                "alchemy_getTokenMetadata",
                [contract],
                allow_unsupported_method=True,
            )
            if metadata is None:
                # Some indexers expose token balances without the optional metadata
                # extension. Fall back to standard ERC-20 calls below in that case.
                metadata = {}
            elif not isinstance(metadata, dict):
                raise ProviderRequestError("The EVM provider returned no token metadata.")
            decimals_value = metadata.get("decimals")
            if isinstance(decimals_value, bool) or not isinstance(decimals_value, int):
                decimals_value = await json_rpc(
                    client,
                    self.rpc_url or "",
                    "eth_call",
                    [{"to": contract, "data": DECIMALS_SELECTOR}, "latest"],
                )
                decimals_value = _decode_uint256(decimals_value)
            if decimals_value < 0 or decimals_value > 255:
                raise ProviderRequestError("An EVM token returned invalid decimal metadata.")

            symbol = metadata.get("symbol")
            if not isinstance(symbol, str) or not symbol.strip():
                try:
                    symbol_data = await json_rpc(
                        client,
                        self.rpc_url or "",
                        "eth_call",
                        [{"to": contract, "data": SYMBOL_SELECTOR}, "latest"],
                    )
                    symbol = _decode_symbol(symbol_data)
                except ProviderRequestError:
                    symbol = ""
            name = metadata.get("name")
            display_symbol = symbol.strip()[:24] if isinstance(symbol, str) else ""
            display_name = name.strip()[:160] if isinstance(name, str) else ""
            return (
                contract,
                token_amounts[contract],
                decimals_value,
                display_symbol,
                display_name,
            )

        metadata_results = await asyncio.gather(
            *(read_metadata(contract) for contract in token_amounts)
        )
        return [result for result in metadata_results if result is not None]
