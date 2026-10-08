import unittest
from unittest.mock import patch

import httpx

from app.connectors.base import ProviderRequestError
from app.connectors.market_data.coingecko import CoinGeckoConnector
from app.connectors.rpc import json_rpc
from app.core.config import settings


class ProviderErrorSanitizationTests(unittest.IsolatedAsyncioTestCase):
    async def test_rpc_http_status_is_actionable_without_exposing_endpoint_or_cause(self) -> None:
        endpoint = "https://rpc.example.test/credential-sentinel"

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(525, text="upstream TLS failure", request=request)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with self.assertRaises(ProviderRequestError) as raised:
                await json_rpc(client, endpoint, "eth_chainId", [])

        self.assertEqual(str(raised.exception), "The configured data provider returned HTTP 525.")
        self.assertNotIn("credential-sentinel", str(raised.exception))
        self.assertIsNone(raised.exception.__cause__)
        self.assertTrue(raised.exception.__suppress_context__)

    async def test_rpc_timeout_hides_request_metadata(self) -> None:
        endpoint = "https://rpc.example.test/credential-sentinel"

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("private transport details", request=request)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with self.assertRaises(ProviderRequestError) as raised:
                await json_rpc(client, endpoint, "eth_chainId", [])

        self.assertEqual(str(raised.exception), "The configured data provider timed out.")
        self.assertNotIn("credential-sentinel", str(raised.exception))
        self.assertIsNone(raised.exception.__cause__)
        self.assertTrue(raised.exception.__suppress_context__)

    async def test_coingecko_http_status_does_not_expose_api_key(self) -> None:
        secret = "coin-gecko-key-sentinel"

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, text="unauthorized", request=request)

        with patch.object(settings, "coingecko_api_key", secret):
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                with self.assertRaises(ProviderRequestError) as raised:
                    await CoinGeckoConnector()._get_json(client, "simple/price", {})

        self.assertEqual(str(raised.exception), "CoinGecko returned HTTP 401.")
        self.assertNotIn(secret, str(raised.exception))
        self.assertIsNone(raised.exception.__cause__)
        self.assertTrue(raised.exception.__suppress_context__)


if __name__ == "__main__":
    unittest.main()
