import unittest
from unittest.mock import patch

from app.connectors.blockchain.networks import supported_networks
from app.core.config import settings
from app.services.wallet_service import wallet_capabilities


class NetworkConfigurationTests(unittest.TestCase):
    def test_alchemy_key_configures_chain_specific_indexer_endpoints(self) -> None:
        with (
            patch.object(settings, "alchemy_api_key", "test-key-that-must-not-leak"),
            patch.object(settings, "ethereum_rpc_url", None),
            patch.object(settings, "evm_rpc_url", None),
            patch.object(settings, "base_rpc_url", "https://base-rpc.example.test"),
            patch.object(settings, "arbitrum_rpc_url", None),
            patch.object(settings, "ethereum_indexed_rpc_url", None),
            patch.object(settings, "base_indexed_rpc_url", None),
            patch.object(settings, "arbitrum_indexed_rpc_url", None),
        ):
            networks = supported_networks()
            capabilities = wallet_capabilities()

        self.assertEqual(
            networks["ethereum"].rpc_url,
            "https://eth-mainnet.g.alchemy.com/v2/test-key-that-must-not-leak",
        )
        self.assertEqual(
            networks["ethereum"].indexed_rpc_url,
            "https://eth-mainnet.g.alchemy.com/v2/test-key-that-must-not-leak",
        )
        self.assertEqual(networks["base"].rpc_url, "https://base-rpc.example.test")
        self.assertEqual(
            networks["base"].indexed_rpc_url,
            "https://base-mainnet.g.alchemy.com/v2/test-key-that-must-not-leak",
        )
        self.assertEqual(
            networks["arbitrum"].rpc_url,
            "https://arb-mainnet.g.alchemy.com/v2/test-key-that-must-not-leak",
        )
        self.assertEqual(networks["ethereum"].alchemy_network_slug, "eth-mainnet")
        self.assertEqual(networks["base"].alchemy_network_slug, "base-mainnet")
        self.assertEqual(networks["arbitrum"].alchemy_network_slug, "arb-mainnet")
        self.assertNotIn("test-key-that-must-not-leak", repr(capabilities))
        self.assertTrue(
            all(
                item.get("dedicatedIndexedProviderConfigured")
                for item in capabilities["networks"]
                if item["id"] in {"ethereum", "base", "arbitrum"}
            )
        )

    def test_per_chain_indexer_endpoints_override_the_shared_alchemy_key(self) -> None:
        with (
            patch.object(settings, "alchemy_api_key", "shared-key"),
            patch.object(
                settings,
                "ethereum_indexed_rpc_url",
                "https://eth-indexer.example.test/rpc",
            ),
            patch.object(
                settings,
                "base_indexed_rpc_url",
                "https://base-indexer.example.test/rpc",
            ),
            patch.object(
                settings,
                "arbitrum_indexed_rpc_url",
                "https://arb-indexer.example.test/rpc",
            ),
        ):
            networks = supported_networks()

        self.assertEqual(
            networks["ethereum"].indexed_rpc_url,
            "https://eth-indexer.example.test/rpc",
        )
        self.assertEqual(
            networks["base"].indexed_rpc_url,
            "https://base-indexer.example.test/rpc",
        )
        self.assertEqual(
            networks["arbitrum"].indexed_rpc_url,
            "https://arb-indexer.example.test/rpc",
        )


if __name__ == "__main__":
    unittest.main()
