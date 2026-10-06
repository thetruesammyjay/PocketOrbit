from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketOrbit API"
    app_env: str = "development"
    database_url: str | None = None
    secret_key: str = "local-only-change-me"
    web_origin: str = "http://localhost:3000"
    solana_rpc_url: str | None = None
    evm_rpc_url: str | None = None
    ethereum_rpc_url: str | None = None
    base_rpc_url: str | None = None
    arbitrum_rpc_url: str | None = None
    ethereum_token_contracts: str = ""
    base_token_contracts: str = ""
    arbitrum_token_contracts: str = ""
    coingecko_api_key: str | None = None
    coingecko_api_base_url: str = "https://api.coingecko.com/api/v3"
    coingecko_api_key_header: str = "x-cg-demo-api-key"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
