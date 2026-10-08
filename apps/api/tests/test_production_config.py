import unittest

from app.core.config import Settings


def _valid_production_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "app_env": "production",
        "database_url": "postgresql+psycopg://user:password@db.example.test/pocketorbit",
        "secret_key": "a" * 64,
        "web_origin": "https://pocketorbit.example",
        "auth_cookie_name": "pocketorbit_session",
        "auth_session_days": 14,
        "max_request_body_bytes": 8 * 1024 * 1024,
        "smtp_host": "smtp.example.test",
        "smtp_port": 587,
        "smtp_from_email": "noreply@pocketorbit.example",
        "smtp_security": "starttls",
        "ethereum_rpc_url": "https://ethereum-rpc.example.test",
        "coingecko_api_base_url": "https://api.coingecko.com/api/v3",
    }
    values.update(overrides)
    return Settings(**values)


class ProductionConfigurationTests(unittest.TestCase):
    def test_production_requires_at_least_one_wallet_provider(self) -> None:
        settings = _valid_production_settings(
            ethereum_rpc_url=None,
            evm_rpc_url=None,
            base_rpc_url=None,
            arbitrum_rpc_url=None,
            solana_rpc_url=None,
            alchemy_api_key=None,
        )

        message = "public wallet RPC endpoint, indexed EVM RPC endpoint, or ALCHEMY_API_KEY"
        with self.assertRaisesRegex(RuntimeError, message):
            settings.validate_runtime_configuration()

    def test_dedicated_alchemy_provider_satisfies_wallet_provider_gate(self) -> None:
        settings = _valid_production_settings(
            ethereum_rpc_url=None,
            evm_rpc_url=None,
            base_rpc_url=None,
            arbitrum_rpc_url=None,
            solana_rpc_url=None,
            alchemy_api_key="test-key",
        )

        settings.validate_runtime_configuration()

    def test_explicit_wallet_rpc_satisfies_wallet_provider_gate(self) -> None:
        settings = _valid_production_settings(
            ethereum_rpc_url=None,
            base_rpc_url="https://base-rpc.example.test",
        )

        settings.validate_runtime_configuration()

    def test_strict_indexed_discovery_can_use_compatible_rpc_without_alchemy_key(self) -> None:
        settings = _valid_production_settings(
            evm_token_discovery="alchemy",
            alchemy_api_key=None,
        )

        settings.validate_runtime_configuration()

    def test_indexed_rpc_endpoint_satisfies_wallet_provider_gate(self) -> None:
        settings = _valid_production_settings(
            evm_token_discovery="alchemy",
            ethereum_rpc_url=None,
            ethereum_indexed_rpc_url="https://ethereum-indexer.example.test/rpc",
        )

        settings.validate_runtime_configuration()

    def test_indexed_rpc_endpoint_must_use_https_in_production(self) -> None:
        settings = _valid_production_settings(
            ethereum_indexed_rpc_url="http://ethereum-indexer.example.test/rpc",
        )

        with self.assertRaisesRegex(RuntimeError, "ETHEREUM_INDEXED_RPC_URL must be a valid HTTPS"):
            settings.validate_runtime_configuration()


if __name__ == "__main__":
    unittest.main()
