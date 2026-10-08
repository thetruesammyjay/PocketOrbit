import asyncio
import json
import unittest
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import httpx

from app.connectors.base import ProviderRequestError
from app.connectors.blockchain.evm import (
    BALANCE_OF_SELECTOR,
    DECIMALS_SELECTOR,
    INDEXER_MAX_PAGES,
    MAX_CONCURRENT_TOKEN_READS,
    SYMBOL_SELECTOR,
    EvmConnector,
)
from app.connectors.blockchain.networks import NetworkConfig
from app.core.config import settings

TOKEN = "0x0000000000000000000000000000000000000001"
WALLET = "0x0000000000000000000000000000000000000002"
TOKEN_AMOUNT = "0x0f4240"
SYMBOL_DATA = (
    "0x"
    + (32).to_bytes(32, "big").hex()
    + (4).to_bytes(32, "big").hex()
    + b"USDC".ljust(32, b"\x00").hex()
)


def _network(
    token_contracts: tuple[str, ...] = (),
    indexed_rpc_url: str | None = None,
    alchemy_network_slug: str | None = None,
) -> NetworkConfig:
    return NetworkConfig(
        id="ethereum",
        name="Ethereum",
        native_symbol="ETH",
        native_name="Ether",
        native_price_id="ethereum",
        price_platform_id="ethereum",
        rpc_url="https://rpc.example.test",
        chain_id=1,
        alchemy_network_slug=alchemy_network_slug,
        indexed_rpc_url=indexed_rpc_url,
        token_contracts=token_contracts,
    )


def _rpc_response(
    request: httpx.Request, result: object = None, error: object = None
) -> httpx.Response:
    payload: dict[str, object] = {"jsonrpc": "2.0", "id": 1}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result
    return httpx.Response(200, json=payload)


class EvmDiscoveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_configured_only_blocks_indexed_fallback_when_chain_rpc_fails(
        self,
    ) -> None:
        requested_hosts: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requested_hosts.append(request.url.host or "")
            if request.url.host == "rpc.example.test":
                return httpx.Response(525, request=request)
            self.fail("configured_only must not contact indexed RPC or Portfolio API providers")

        connector = EvmConnector(
            _network(
                indexed_rpc_url="https://indexer.example.test/v2/redacted",
                alchemy_network_slug="eth-mainnet",
            )
        )
        with (
            patch.object(settings, "evm_token_discovery", "configured_only"),
            patch.object(settings, "alchemy_api_key", "test-portfolio-key"),
        ):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                with self.assertRaisesRegex(
                    ProviderRequestError,
                    "configured Ethereum RPC could not be used.*HTTP 525",
                ):
                    await connector.get_balances(WALLET, client)

        self.assertEqual(requested_hosts, ["rpc.example.test"])
        self.assertFalse(connector.uses_indexed_rpc_fallback)
        self.assertFalse(connector.uses_alchemy_portfolio_api)

    async def test_failed_alchemy_fallback_gives_actionable_sanitized_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            rpc = json.loads(request.content)
            self.assertEqual(rpc["method"], "eth_chainId")
            if request.url.host == "rpc.example.test":
                return httpx.Response(525, request=request)
            self.assertEqual(request.url.host, "indexer.example.test")
            return httpx.Response(403, request=request)

        connector = EvmConnector(
            _network(indexed_rpc_url="https://indexer.example.test/v2/redacted")
        )
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with self.assertRaisesRegex(
                ProviderRequestError,
                "indexed RPC fallback could not be used.*HTTP 403.*Portfolio API fallback",
            ) as raised:
                await connector.get_balances(WALLET, client)

        self.assertNotIn("redacted", str(raised.exception))

    async def test_chain_reads_fall_back_to_dedicated_alchemy_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            rpc = json.loads(request.content)
            method = rpc["method"]
            if request.url.host == "rpc.example.test":
                self.assertEqual(method, "eth_chainId")
                return httpx.Response(525, request=request)

            self.assertEqual(request.url.host, "indexer.example.test")
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "eth_blockNumber":
                return _rpc_response(request, "0x123")
            if method == "eth_getBalance":
                return _rpc_response(request, "0x0")
            if method == "alchemy_getTokenBalances":
                return _rpc_response(request, {"tokenBalances": []})
            self.fail(f"Unexpected RPC method: {method}")

        connector = EvmConnector(
            _network(indexed_rpc_url="https://indexer.example.test/v2/redacted")
        )
        with patch.object(settings, "evm_token_discovery", "alchemy"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        self.assertTrue(connector.uses_indexed_rpc_fallback)
        self.assertTrue(connector.uses_indexed_token_discovery)
        self.assertEqual(len(balances), 1)

    async def test_dedicated_indexer_keeps_chain_reads_on_configured_rpc(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            rpc = json.loads(request.content)
            method = rpc["method"]
            if request.url.host == "rpc.example.test":
                if method == "eth_chainId":
                    return _rpc_response(request, "0x1")
                if method == "eth_blockNumber":
                    return _rpc_response(request, "0x123")
                if method == "eth_getBalance":
                    return _rpc_response(request, "0x0")
            self.assertEqual(request.url.host, "indexer.example.test")
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "alchemy_getTokenBalances":
                return _rpc_response(
                    request,
                    {"tokenBalances": [{"contractAddress": TOKEN, "tokenBalance": TOKEN_AMOUNT}]},
                )
            if method == "alchemy_getTokenMetadata":
                return _rpc_response(
                    request,
                    {"decimals": 6, "symbol": "USDC", "name": "USD Coin"},
                )
            self.fail(f"Unexpected RPC method: {method}")

        connector = EvmConnector(
            _network(indexed_rpc_url="https://indexer.example.test/v2/redacted")
        )
        with patch.object(settings, "evm_token_discovery", "alchemy"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        token_balance = next(balance for balance in balances if balance.contract_address)
        self.assertEqual(token_balance.symbol, "USDC")
        self.assertTrue(connector.uses_indexed_token_discovery)

    async def test_indexed_rpc_must_match_the_selected_network(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            rpc = json.loads(request.content)
            method = rpc["method"]
            if request.url.host == "rpc.example.test":
                if method == "eth_chainId":
                    return _rpc_response(request, "0x1")
                if method == "eth_blockNumber":
                    return _rpc_response(request, "0x123")
                if method == "eth_getBalance":
                    return _rpc_response(request, "0x0")
            if request.url.host == "indexer.example.test" and method == "eth_chainId":
                return _rpc_response(request, "0xa4b1")
            self.fail(f"Unexpected RPC request: {rpc}")

        connector = EvmConnector(
            _network(indexed_rpc_url="https://indexer.example.test/v2/redacted")
        )
        with patch.object(settings, "evm_token_discovery", "alchemy"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                with self.assertRaisesRegex(
                    ProviderRequestError,
                    "indexed RPC endpoint is not connected to Ethereum",
                ):
                    await connector.get_balances(WALLET, client)

    async def test_indexed_discovery_reads_tokens_and_does_not_claim_native_block(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            rpc = json.loads(request.content)
            method = rpc["method"]
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "eth_blockNumber":
                return _rpc_response(request, "0x123")
            if method == "eth_getBalance":
                return _rpc_response(request, "0xde0b6b3a7640000")
            if method == "alchemy_getTokenBalances":
                return _rpc_response(
                    request,
                    {"tokenBalances": [{"contractAddress": TOKEN, "tokenBalance": TOKEN_AMOUNT}]},
                )
            if method == "alchemy_getTokenMetadata":
                return _rpc_response(
                    request,
                    {"decimals": 6, "symbol": "USDC", "name": "USD Coin"},
                )
            self.fail(f"Unexpected RPC method: {method}")

        connector = EvmConnector(_network())
        with patch.object(settings, "evm_token_discovery", "alchemy"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        token_balance = next(balance for balance in balances if balance.contract_address)
        native_balance = next(balance for balance in balances if not balance.contract_address)
        self.assertTrue(connector.uses_indexed_token_discovery)
        self.assertEqual(token_balance.symbol, "USDC")
        self.assertEqual(token_balance.name, "USD Coin")
        self.assertEqual(token_balance.quantity, Decimal("1"))
        self.assertIsNone(token_balance.block_reference)
        self.assertEqual(native_balance.quantity, Decimal("1"))
        self.assertEqual(native_balance.block_reference, "block:291")

    async def test_auto_mode_falls_back_to_configured_contracts(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            rpc = json.loads(request.content)
            method = rpc["method"]
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "eth_blockNumber":
                return _rpc_response(request, "0x10")
            if method == "eth_getBalance":
                return _rpc_response(request, "0x0")
            if method == "alchemy_getTokenBalances":
                return _rpc_response(request, error={"code": -32601, "message": "method not found"})
            if method == "eth_call":
                selector = rpc["params"][0]["data"][:10]
                if selector == BALANCE_OF_SELECTOR:
                    return _rpc_response(request, TOKEN_AMOUNT)
                if selector == DECIMALS_SELECTOR:
                    return _rpc_response(request, "0x6")
                if selector == SYMBOL_SELECTOR:
                    return _rpc_response(request, SYMBOL_DATA)
            self.fail(f"Unexpected RPC request: {rpc}")

        connector = EvmConnector(_network((TOKEN,)))
        with patch.object(settings, "evm_token_discovery", "auto"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        token_balance = next(balance for balance in balances if balance.contract_address)
        self.assertFalse(connector.uses_indexed_token_discovery)
        self.assertEqual(token_balance.symbol, "USDC")
        self.assertEqual(token_balance.quantity, Decimal("1"))
        self.assertEqual(token_balance.block_reference, "block:16")

    async def test_configured_contract_reads_have_bounded_concurrency(self) -> None:
        contracts = tuple(f"0x{index:040x}" for index in range(20))
        active_requests = 0
        maximum_active_requests = 0

        async def fake_json_rpc(
            client: httpx.AsyncClient,
            endpoint: str,
            method: str,
            params: list[object],
            *,
            allow_unsupported_method: bool = False,
        ) -> object:
            nonlocal active_requests, maximum_active_requests
            active_requests += 1
            maximum_active_requests = max(maximum_active_requests, active_requests)
            try:
                await asyncio.sleep(0)
                selector = params[0]["data"][:10]  # type: ignore[index]
                if selector == BALANCE_OF_SELECTOR:
                    return TOKEN_AMOUNT
                if selector == DECIMALS_SELECTOR:
                    return "0x6"
                if selector == SYMBOL_SELECTOR:
                    return SYMBOL_DATA
                self.fail(f"Unexpected selector: {selector}")
            finally:
                active_requests -= 1

        connector = EvmConnector(_network(contracts))
        with (
            patch.object(settings, "evm_token_discovery", "configured_only"),
            patch(
                "app.connectors.blockchain.evm.json_rpc",
                new=AsyncMock(side_effect=fake_json_rpc),
            ),
        ):
            async with httpx.AsyncClient() as client:
                balances = await connector._read_tokens(client, WALLET, "0x1")

        self.assertEqual(len(balances), len(contracts))
        self.assertLessEqual(maximum_active_requests, MAX_CONCURRENT_TOKEN_READS * 2)

    async def test_auto_mode_falls_back_when_indexed_method_is_http_forbidden(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            rpc = json.loads(request.content)
            method = rpc["method"]
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "eth_blockNumber":
                return _rpc_response(request, "0x10")
            if method == "eth_getBalance":
                return _rpc_response(request, "0x0")
            if method == "alchemy_getTokenBalances":
                return httpx.Response(403, request=request)
            if method == "eth_call":
                selector = rpc["params"][0]["data"][:10]
                if selector == BALANCE_OF_SELECTOR:
                    return _rpc_response(request, TOKEN_AMOUNT)
                if selector == DECIMALS_SELECTOR:
                    return _rpc_response(request, "0x6")
                if selector == SYMBOL_SELECTOR:
                    return _rpc_response(request, SYMBOL_DATA)
            self.fail(f"Unexpected RPC request: {rpc}")

        connector = EvmConnector(_network((TOKEN,)))
        with patch.object(settings, "evm_token_discovery", "auto"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        token_balance = next(balance for balance in balances if balance.contract_address)
        self.assertFalse(connector.uses_indexed_token_discovery)
        self.assertEqual(token_balance.symbol, "USDC")
        self.assertEqual(token_balance.quantity, Decimal("1"))

    async def test_indexed_metadata_failure_skips_only_that_token(self) -> None:
        broken_token = "0x0000000000000000000000000000000000000003"

        def handler(request: httpx.Request) -> httpx.Response:
            rpc = json.loads(request.content)
            method = rpc["method"]
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "eth_blockNumber":
                return _rpc_response(request, "0x123")
            if method == "eth_getBalance":
                return _rpc_response(request, "0x0")
            if method == "alchemy_getTokenBalances":
                return _rpc_response(
                    request,
                    {
                        "tokenBalances": [
                            {"contractAddress": TOKEN, "tokenBalance": TOKEN_AMOUNT},
                            {"contractAddress": broken_token, "tokenBalance": TOKEN_AMOUNT},
                        ]
                    },
                )
            if method == "alchemy_getTokenMetadata":
                contract = rpc["params"][0]
                metadata = (
                    {"decimals": 6, "symbol": "USDC", "name": "USD Coin"}
                    if contract == TOKEN
                    else {"symbol": "BROKEN", "name": "Broken Token"}
                )
                return _rpc_response(request, metadata)
            if method == "eth_call":
                return _rpc_response(
                    request,
                    error={"code": -32000, "message": "execution reverted"},
                )
            self.fail(f"Unexpected RPC method: {method}")

        connector = EvmConnector(_network())
        with patch.object(settings, "evm_token_discovery", "alchemy"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        discovered_tokens = [balance for balance in balances if balance.contract_address]
        self.assertEqual([balance.contract_address for balance in discovered_tokens], [TOKEN])
        self.assertEqual(connector.indexed_token_failures, 1)

    async def test_indexed_token_error_without_contract_skips_only_that_entry(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            rpc = json.loads(request.content)
            method = rpc["method"]
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "eth_blockNumber":
                return _rpc_response(request, "0x123")
            if method == "eth_getBalance":
                return _rpc_response(request, "0x0")
            if method == "alchemy_getTokenBalances":
                return _rpc_response(
                    request,
                    {
                        "tokenBalances": [
                            {"error": "token balance unavailable"},
                            {"contractAddress": TOKEN, "tokenBalance": TOKEN_AMOUNT},
                        ]
                    },
                )
            if method == "alchemy_getTokenMetadata":
                return _rpc_response(
                    request,
                    {"decimals": 6, "symbol": "USDC", "name": "USD Coin"},
                )
            self.fail(f"Unexpected RPC method: {method}")

        connector = EvmConnector(_network())
        with patch.object(settings, "evm_token_discovery", "alchemy"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        discovered_tokens = [balance for balance in balances if balance.contract_address]
        self.assertEqual([balance.contract_address for balance in discovered_tokens], [TOKEN])
        self.assertEqual(connector.indexed_token_failures, 1)

    async def test_token_quantity_beyond_database_scale_is_preserved_exactly(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            rpc = json.loads(request.content)
            method = rpc["method"]
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "eth_blockNumber":
                return _rpc_response(request, "0x123")
            if method == "eth_getBalance":
                return _rpc_response(request, "0x0")
            if method == "alchemy_getTokenBalances":
                return _rpc_response(
                    request,
                    {"tokenBalances": [{"contractAddress": TOKEN, "tokenBalance": "0x1"}]},
                )
            if method == "alchemy_getTokenMetadata":
                return _rpc_response(request, {"decimals": 24, "symbol": "TINY", "name": "Tiny"})
            self.fail(f"Unexpected RPC method: {method}")

        connector = EvmConnector(_network())
        with patch.object(settings, "evm_token_discovery", "alchemy"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        tiny_token = next(balance for balance in balances if balance.contract_address == TOKEN)
        self.assertEqual(tiny_token.quantity, Decimal("0.000000000000000000000001"))

    async def test_large_raw_balance_conversion_does_not_round_in_decimal_context(self) -> None:
        raw_amount = 1000000000000000000000000000001

        def handler(request: httpx.Request) -> httpx.Response:
            rpc = json.loads(request.content)
            method = rpc["method"]
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "eth_blockNumber":
                return _rpc_response(request, "0x123")
            if method == "eth_getBalance":
                return _rpc_response(request, "0x0")
            if method == "alchemy_getTokenBalances":
                return _rpc_response(
                    request,
                    {
                        "tokenBalances": [
                            {"contractAddress": TOKEN, "tokenBalance": hex(raw_amount)}
                        ]
                    },
                )
            if method == "alchemy_getTokenMetadata":
                return _rpc_response(request, {"decimals": 18, "symbol": "TOK", "name": "Token"})
            self.fail(f"Unexpected RPC method: {method}")

        connector = EvmConnector(_network())
        with patch.object(settings, "evm_token_discovery", "alchemy"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        token_balance = next(balance for balance in balances if balance.contract_address == TOKEN)
        self.assertEqual(
            token_balance.quantity,
            Decimal("1000000000000.000000000000000001"),
        )

    async def test_indexed_metadata_falls_back_to_standard_calls_when_http_forbidden(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            rpc = json.loads(request.content)
            method = rpc["method"]
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "eth_blockNumber":
                return _rpc_response(request, "0x123")
            if method == "eth_getBalance":
                return _rpc_response(request, "0x0")
            if method == "alchemy_getTokenBalances":
                return _rpc_response(
                    request,
                    {"tokenBalances": [{"contractAddress": TOKEN, "tokenBalance": TOKEN_AMOUNT}]},
                )
            if method == "alchemy_getTokenMetadata":
                return httpx.Response(403, request=request)
            if method == "eth_call":
                selector = rpc["params"][0]["data"][:10]
                if selector == DECIMALS_SELECTOR:
                    return _rpc_response(request, "0x6")
                if selector == SYMBOL_SELECTOR:
                    return _rpc_response(request, SYMBOL_DATA)
            self.fail(f"Unexpected RPC request: {rpc}")

        connector = EvmConnector(_network())
        with patch.object(settings, "evm_token_discovery", "alchemy"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        token_balance = next(balance for balance in balances if balance.contract_address)
        self.assertTrue(connector.uses_indexed_token_discovery)
        self.assertEqual(token_balance.symbol, "USDC")
        self.assertEqual(token_balance.quantity, Decimal("1"))
        self.assertEqual(connector.indexed_token_failures, 0)

    async def test_portfolio_api_discovers_tokens_when_indexed_rpc_method_is_unavailable(
        self,
    ) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.host == "api.g.alchemy.com":
                body = json.loads(request.content)
                self.assertEqual(body["addresses"][0]["networks"], ["eth-mainnet"])
                self.assertTrue(body["withMetadata"])
                self.assertFalse(body["includeNativeTokens"])
                return httpx.Response(
                    200,
                    json={
                        "data": {
                            "tokens": [
                                {
                                    "address": WALLET,
                                    "network": "eth-mainnet",
                                    "tokenAddress": TOKEN,
                                    "tokenBalance": TOKEN_AMOUNT,
                                    "tokenMetadata": {
                                        "decimals": 6,
                                        "symbol": "USDC",
                                        "name": "USD Coin",
                                    },
                                }
                            ]
                        }
                    },
                )

            rpc = json.loads(request.content)
            method = rpc["method"]
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "eth_blockNumber":
                return _rpc_response(request, "0x123")
            if method == "eth_getBalance":
                return _rpc_response(request, "0x0")
            if method == "alchemy_getTokenBalances":
                return _rpc_response(
                    request,
                    error={"code": -32601, "message": "method not found"},
                )
            self.fail(f"Unexpected RPC method: {method}")

        connector = EvmConnector(_network(alchemy_network_slug="eth-mainnet"))
        with (
            patch.object(settings, "evm_token_discovery", "auto"),
            patch.object(settings, "alchemy_api_key", "test-portfolio-key"),
        ):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        token_balance = next(balance for balance in balances if balance.contract_address)
        self.assertEqual(token_balance.symbol, "USDC")
        self.assertEqual(token_balance.name, "USD Coin")
        self.assertEqual(token_balance.quantity, Decimal("1"))
        self.assertIsNone(token_balance.block_reference)
        self.assertTrue(connector.uses_indexed_token_discovery)
        self.assertTrue(connector.uses_alchemy_portfolio_api)

    async def test_portfolio_api_supplies_native_and_token_balances_when_chain_rpcs_fail(
        self,
    ) -> None:
        indexed_endpoint = "https://indexer.example.test/v2/redacted"

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.host == "rpc.example.test":
                return httpx.Response(525, request=request)
            if request.url.host == "indexer.example.test":
                return httpx.Response(403, request=request)
            if request.url.host == "api.g.alchemy.com":
                body = json.loads(request.content)
                self.assertTrue(body["includeNativeTokens"])
                return httpx.Response(
                    200,
                    json={
                        "data": {
                            "tokens": [
                                {
                                    "address": WALLET,
                                    "network": "eth-mainnet",
                                    "tokenAddress": None,
                                    "tokenBalance": "0xde0b6b3a7640000",
                                    "tokenMetadata": {"decimals": 18},
                                },
                                {
                                    "address": WALLET,
                                    "network": "eth-mainnet",
                                    "tokenAddress": TOKEN,
                                    "tokenBalance": TOKEN_AMOUNT,
                                    "tokenMetadata": {
                                        "decimals": 6,
                                        "symbol": "USDC",
                                        "name": "USD Coin",
                                    },
                                },
                            ]
                        }
                    },
                )
            self.fail(f"Unexpected request host: {request.url.host}")

        connector = EvmConnector(
            _network(
                indexed_rpc_url=indexed_endpoint,
                alchemy_network_slug="eth-mainnet",
            )
        )
        with patch.object(settings, "alchemy_api_key", "test-portfolio-key"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        native = next(balance for balance in balances if balance.contract_address is None)
        token = next(balance for balance in balances if balance.contract_address)
        self.assertEqual(native.quantity, Decimal("1"))
        self.assertEqual(token.quantity, Decimal("1"))
        self.assertIsNone(native.block_reference)
        self.assertIsNone(token.block_reference)
        self.assertTrue(connector.uses_alchemy_portfolio_chain_fallback)
        self.assertTrue(connector.uses_alchemy_portfolio_api)
        self.assertTrue(connector.uses_indexed_token_discovery)

    async def test_portfolio_api_partial_error_is_not_counted_as_a_skipped_token(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.host == "api.g.alchemy.com":
                return httpx.Response(
                    200,
                    json={
                        "data": {
                            "tokens": [
                                {
                                    "address": WALLET,
                                    "network": "eth-mainnet",
                                    "tokenAddress": TOKEN,
                                    "tokenBalance": TOKEN_AMOUNT,
                                    "tokenMetadata": {
                                        "decimals": 6,
                                        "symbol": "USDC",
                                        "name": "USD Coin",
                                    },
                                }
                            ]
                        },
                        "error": {
                            "partialErrors": [
                                {"network": "eth-mainnet", "message": "partial"}
                            ]
                        },
                    },
                )

            rpc = json.loads(request.content)
            method = rpc["method"]
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "eth_blockNumber":
                return _rpc_response(request, "0x123")
            if method == "eth_getBalance":
                return _rpc_response(request, "0x0")
            if method == "alchemy_getTokenBalances":
                return _rpc_response(request, error={"code": -32601, "message": "method not found"})
            self.fail(f"Unexpected RPC method: {method}")

        connector = EvmConnector(_network(alchemy_network_slug="eth-mainnet"))
        with (
            patch.object(settings, "evm_token_discovery", "auto"),
            patch.object(settings, "alchemy_api_key", "test-portfolio-key"),
        ):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        self.assertEqual(len(balances), 2)
        self.assertEqual(connector.indexed_token_failures, 0)
        self.assertEqual(connector.indexed_provider_partial_errors, 1)

    async def test_portfolio_api_paginates_and_stops_at_the_token_cap(self) -> None:
        page_requests = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal page_requests
            body = json.loads(request.content)
            page_requests += 1
            if page_requests == 1:
                self.assertNotIn("pageKey", body)
                start = 1
                count = 100
                next_page = "next-page"
            else:
                self.assertEqual(body.get("pageKey"), "next-page")
                start = 101
                count = 101
                next_page = "later-page"
            tokens = [
                {
                    "address": WALLET,
                    "network": "eth-mainnet",
                    "tokenAddress": f"0x{index:040x}",
                    "tokenBalance": "0x1",
                    "tokenMetadata": {"decimals": 18, "symbol": "TOK", "name": "Token"},
                }
                for index in range(start, start + count)
            ]
            return httpx.Response(
                200,
                json={"data": {"tokens": tokens, "pageKey": next_page}},
            )

        connector = EvmConnector(_network(alchemy_network_slug="eth-mainnet"))
        with patch.object(settings, "alchemy_api_key", "test-portfolio-key"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                assets = await connector._read_alchemy_portfolio_api_assets(
                    client,
                    WALLET,
                    include_native=False,
                )

        self.assertIsNotNone(assets)
        self.assertEqual(len(assets or []), 200)
        self.assertEqual(page_requests, 2)
        self.assertTrue(connector.indexed_token_limit_reached)
        self.assertEqual(connector.indexed_token_limit_skipped, 1)

    async def test_portfolio_api_caps_before_bounded_decimal_fallback_reads(self) -> None:
        tokens = [
            {
                "address": WALLET,
                "network": "eth-mainnet",
                "tokenAddress": f"0x{index:040x}",
                "tokenBalance": "0x1",
                "tokenMetadata": {"symbol": "TOK"},
            }
            for index in range(1, 202)
        ]
        active_reads = 0
        maximum_active_reads = 0

        async def fake_json_rpc(
            client: httpx.AsyncClient,
            endpoint: str,
            method: str,
            params: list[object],
            *,
            allow_unsupported_method: bool = False,
        ) -> object:
            nonlocal active_reads, maximum_active_reads
            self.assertEqual(method, "eth_call")
            active_reads += 1
            maximum_active_reads = max(maximum_active_reads, active_reads)
            try:
                await asyncio.sleep(0)
                return "0x6"
            finally:
                active_reads -= 1

        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.host, "api.g.alchemy.com")
            return httpx.Response(
                200,
                json={"data": {"tokens": tokens, "pageKey": "later-page"}},
            )

        connector = EvmConnector(_network(alchemy_network_slug="eth-mainnet"))
        rpc_mock = AsyncMock(side_effect=fake_json_rpc)
        with (
            patch.object(settings, "alchemy_api_key", "test-portfolio-key"),
            patch("app.connectors.blockchain.evm.json_rpc", new=rpc_mock),
        ):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                assets = await connector._read_alchemy_portfolio_api_assets(
                    client,
                    WALLET,
                    include_native=False,
                )

        self.assertEqual(len(assets or []), 200)
        self.assertEqual(rpc_mock.await_count, 200)
        self.assertGreater(maximum_active_reads, 1)
        self.assertLessEqual(maximum_active_reads, MAX_CONCURRENT_TOKEN_READS)
        self.assertTrue(connector.indexed_token_limit_reached)
        self.assertEqual(connector.indexed_token_limit_skipped, 1)

    async def test_indexer_caps_a_wallet_over_the_token_limit_and_marks_partial(self) -> None:
        tokens = [
            {"contractAddress": f"0x{index:040x}", "tokenBalance": "0x1"} for index in range(1, 202)
        ]

        def handler(request: httpx.Request) -> httpx.Response:
            rpc = json.loads(request.content)
            method = rpc["method"]
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "eth_blockNumber":
                return _rpc_response(request, "0x123")
            if method == "eth_getBalance":
                return _rpc_response(request, "0x0")
            if method == "alchemy_getTokenBalances":
                return _rpc_response(request, {"tokenBalances": tokens})
            if method == "alchemy_getTokenMetadata":
                return _rpc_response(
                    request,
                    {"decimals": 18, "symbol": "TOK", "name": "Token"},
                )
            self.fail(f"Unexpected RPC method: {method}")

        connector = EvmConnector(_network())
        with patch.object(settings, "evm_token_discovery", "alchemy"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        token_balances = [balance for balance in balances if balance.contract_address]
        self.assertEqual(len(token_balances), 200)
        self.assertTrue(connector.uses_indexed_token_discovery)
        self.assertEqual(connector.indexed_token_failures, 0)
        self.assertTrue(connector.indexed_token_limit_reached)
        self.assertEqual(connector.indexed_token_limit_skipped, 1)

    async def test_indexer_stops_after_a_page_proves_the_token_limit_was_exceeded(self) -> None:
        page_requests = 0
        metadata_requests = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal page_requests, metadata_requests
            rpc = json.loads(request.content)
            method = rpc["method"]
            if method == "alchemy_getTokenBalances":
                page_requests += 1
                start = (page_requests - 1) * 100 + 1
                tokens = [
                    {"contractAddress": f"0x{index:040x}", "tokenBalance": "0x1"}
                    for index in range(start, start + 100)
                ]
                return _rpc_response(
                    request,
                    {"tokenBalances": tokens, "pageKey": f"page-{page_requests}"},
                )
            if method == "alchemy_getTokenMetadata":
                metadata_requests += 1
                return _rpc_response(
                    request,
                    {"decimals": 18, "symbol": "TOK", "name": "Token"},
                )
            self.fail(f"Unexpected RPC method: {method}")

        connector = EvmConnector(_network())
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            discovered = await connector._read_indexed_tokens(client, WALLET)

        self.assertIsNotNone(discovered)
        self.assertEqual(len(discovered or []), 200)
        self.assertEqual(page_requests, 3)
        self.assertEqual(metadata_requests, 200)
        self.assertTrue(connector.indexed_token_limit_reached)
        self.assertEqual(connector.indexed_token_limit_skipped, 100)

    async def test_indexer_page_limit_returns_a_truncated_partial_result(self) -> None:
        page_requests = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal page_requests
            rpc = json.loads(request.content)
            method = rpc["method"]
            if method == "eth_chainId":
                return _rpc_response(request, "0x1")
            if method == "eth_blockNumber":
                return _rpc_response(request, "0x123")
            if method == "eth_getBalance":
                return _rpc_response(request, "0x0")
            if method == "alchemy_getTokenBalances":
                page_requests += 1
                return _rpc_response(
                    request,
                    {"tokenBalances": [], "pageKey": f"page-{page_requests}"},
                )
            self.fail(f"Unexpected RPC method: {method}")

        connector = EvmConnector(_network())
        with patch.object(settings, "evm_token_discovery", "alchemy"):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                balances = await connector.get_balances(WALLET, client)

        self.assertEqual(page_requests, INDEXER_MAX_PAGES)
        self.assertEqual(len(balances), 1)
        self.assertTrue(connector.uses_indexed_token_discovery)
        self.assertTrue(connector.indexed_token_discovery_truncated)


if __name__ == "__main__":
    unittest.main()
