import unittest
from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.connectors.base import NormalizedBalance
from app.connectors.blockchain.evm import EvmConnector
from app.connectors.blockchain.networks import NetworkConfig
from app.schemas.common import QualityStatus
from app.services.wallet_service import refresh_public_wallet

WALLET = "0x0000000000000000000000000000000000000002"


class WalletQualityTests(unittest.IsolatedAsyncioTestCase):
    async def test_token_limit_withholds_total_and_explains_partial_coverage(self) -> None:
        network = NetworkConfig(
            id="ethereum",
            name="Ethereum",
            native_symbol="ETH",
            native_name="Ether",
            native_price_id="ethereum",
            price_platform_id="ethereum",
            rpc_url="https://rpc.example.test",
            chain_id=1,
        )
        connector = EvmConnector(network)
        connector.uses_indexed_token_discovery = True
        connector.indexed_token_limit_reached = True
        connector.indexed_token_limit_skipped = 12

        with (
            patch(
                "app.services.wallet_service.supported_networks",
                return_value={"ethereum": network},
            ),
            patch("app.services.wallet_service._connector", return_value=connector),
            patch.object(connector, "get_balances", new=AsyncMock(return_value=[])),
            patch(
                "app.services.wallet_service.resolve_prices",
                new=AsyncMock(return_value=SimpleNamespace(quotes={}, warnings=[])),
            ),
        ):
            response = await refresh_public_wallet("ethereum", WALLET)

        self.assertEqual(response.quality, QualityStatus.PARTIAL)
        self.assertIsNone(response.total_value)
        self.assertTrue(
            any(
                "200 positive-token limit" in warning and "12 additional" in warning
                for warning in response.warnings
            )
        )

    async def test_provider_partial_error_withholds_total_and_explains_coverage(self) -> None:
        network = NetworkConfig(
            id="ethereum",
            name="Ethereum",
            native_symbol="ETH",
            native_name="Ether",
            native_price_id="ethereum",
            price_platform_id="ethereum",
            rpc_url="https://rpc.example.test",
            chain_id=1,
        )
        connector = EvmConnector(network)
        connector.uses_indexed_token_discovery = True
        connector.indexed_provider_partial_errors = 1

        with (
            patch(
                "app.services.wallet_service.supported_networks",
                return_value={"ethereum": network},
            ),
            patch("app.services.wallet_service._connector", return_value=connector),
            patch.object(connector, "get_balances", new=AsyncMock(return_value=[])),
            patch(
                "app.services.wallet_service.resolve_prices",
                new=AsyncMock(return_value=SimpleNamespace(quotes={}, warnings=[])),
            ),
        ):
            response = await refresh_public_wallet("ethereum", WALLET)

        self.assertEqual(response.quality, QualityStatus.PARTIAL)
        self.assertIsNone(response.total_value)
        self.assertTrue(
            any("reported 1 partial network result" in warning for warning in response.warnings)
        )

    async def test_unstorable_evm_quantity_withholds_total_and_explains_omission(self) -> None:
        network = NetworkConfig(
            id="ethereum",
            name="Ethereum",
            native_symbol="ETH",
            native_name="Ether",
            native_price_id="ethereum",
            price_platform_id="ethereum",
            rpc_url="https://rpc.example.test",
            chain_id=1,
        )
        connector = EvmConnector(network)
        connector.uses_indexed_token_discovery = True
        unpersistable_balance = NormalizedBalance(
            asset_id=f"ethereum:{WALLET}",
            symbol="TINY",
            name="Tiny token",
            network_id="ethereum",
            quantity=Decimal("0.000000000000000000000001"),
            contract_address=WALLET,
            decimals=24,
            source_record_ids=(WALLET,),
            retrieved_at=datetime.now(UTC),
        )

        with (
            patch(
                "app.services.wallet_service.supported_networks",
                return_value={"ethereum": network},
            ),
            patch("app.services.wallet_service._connector", return_value=connector),
            patch.object(
                connector,
                "get_balances",
                new=AsyncMock(return_value=[unpersistable_balance]),
            ),
            patch(
                "app.services.wallet_service.resolve_prices",
                new=AsyncMock(return_value=SimpleNamespace(quotes={}, warnings=[])),
            ),
        ):
            response = await refresh_public_wallet("ethereum", WALLET)

        self.assertEqual(response.quality, QualityStatus.PARTIAL)
        self.assertIsNone(response.total_value)
        self.assertEqual(response.balances, [])
        self.assertTrue(
            any("exceeded the stored quantity precision" in warning for warning in response.warnings)
        )


if __name__ == "__main__":
    unittest.main()
