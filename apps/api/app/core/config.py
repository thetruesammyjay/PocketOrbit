import ipaddress
from functools import lru_cache
from urllib.parse import urlparse

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketOrbit API"
    app_env: str = "development"
    database_url: str | None = None
    secret_key: str = "local-only-change-me"
    web_origin: str = "http://localhost:3000"
    auth_cookie_name: str = "pocketorbit_session"
    auth_cookie_domain: str | None = None
    auth_cookie_samesite: str = "lax"
    auth_session_days: int = 14
    admin_emails: str = ""
    admin_password: str = ""
    max_request_body_bytes: int = 8 * 1024 * 1024
    trusted_proxy_cidrs: str = ""
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_security: str = "starttls"
    evm_token_discovery: str = "auto"
    solana_rpc_url: str | None = None
    solana_rpc_fallback_url: str = "https://solana-rpc.publicnode.com"
    evm_rpc_url: str | None = None
    ethereum_rpc_url: str | None = None
    base_rpc_url: str | None = None
    arbitrum_rpc_url: str | None = None
    ethereum_indexed_rpc_url: str | None = None
    base_indexed_rpc_url: str | None = None
    arbitrum_indexed_rpc_url: str | None = None
    alchemy_api_key: str | None = None
    ethereum_token_contracts: str = ""
    base_token_contracts: str = ""
    arbitrum_token_contracts: str = ""
    coingecko_api_key: str | None = None
    coingecko_api_base_url: str = "https://api.coingecko.com/api/v3"
    coingecko_api_key_header: str = "x-cg-demo-api-key"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @field_validator("auth_cookie_domain", mode="before")
    @classmethod
    def empty_cookie_domain_is_host_only(cls, value: str | None) -> str | None:
        if value is None or not str(value).strip():
            return None
        return str(value).strip()

    def validate_runtime_configuration(self) -> None:
        """Reject unsafe or incomplete settings before serving production traffic."""
        if self.evm_token_discovery.strip().lower() not in {"auto", "alchemy", "configured_only"}:
            raise RuntimeError("EVM_TOKEN_DISCOVERY must be auto, alchemy, or configured_only")
        if self.app_env.strip().lower() not in {"production", "prod"}:
            return

        problems: list[str] = []
        secret = self.secret_key.strip()
        if len(secret) < 32 or secret in {
            "local-only-change-me",
            "replace-this-for-local-development",
        }:
            problems.append("SECRET_KEY must be a unique value with at least 32 characters")
        database_url = (self.database_url or "").strip().lower()
        if not database_url.startswith(("postgres://", "postgresql://", "postgresql+psycopg://")):
            problems.append("DATABASE_URL must use PostgreSQL")
        if self.auth_session_days < 1 or self.auth_session_days > 30:
            problems.append("AUTH_SESSION_DAYS must be between 1 and 30")
        admin_emails = [
            address.strip().lower()
            for address in self.admin_emails.split(",")
            if address.strip()
        ]
        if not admin_emails or any("@" not in address for address in admin_emails):
            problems.append(
                "ADMIN_EMAILS must list one or more valid administrator email addresses"
            )
        if self.max_request_body_bytes < 5 * 1024 * 1024 + 64 * 1024:
            problems.append("MAX_REQUEST_BODY_BYTES must allow a 5 MB CSV plus multipart overhead")
        if self.max_request_body_bytes > 64 * 1024 * 1024:
            problems.append("MAX_REQUEST_BODY_BYTES must not exceed 64 MiB")
        if self.auth_cookie_samesite.lower() not in {"lax", "strict", "none"}:
            problems.append("AUTH_COOKIE_SAMESITE must be Lax, Strict, or None")
        if len(self.admin_password) < 12:
            problems.append("ADMIN_PASSWORD must contain at least 12 characters")
        smtp_is_configured = any(
            value and value.strip()
            for value in (
                self.smtp_host,
                self.smtp_username,
                self.smtp_password,
                self.smtp_from_email,
            )
        )
        if smtp_is_configured:
            if not self.smtp_host or not self.smtp_from_email:
                problems.append("SMTP_HOST and SMTP_FROM_EMAIL must be configured together")
            if self.smtp_security.strip().lower() not in {"starttls", "ssl"}:
                problems.append("SMTP_SECURITY must be starttls or ssl")
            if not 1 <= self.smtp_port <= 65535:
                problems.append("SMTP_PORT must be between 1 and 65535")
            if bool(self.smtp_username) != bool(self.smtp_password):
                problems.append("SMTP_USERNAME and SMTP_PASSWORD must be configured together")
        wallet_rpc_endpoints = (
            self.solana_rpc_url,
            self.solana_rpc_fallback_url,
            self.evm_rpc_url,
            self.ethereum_rpc_url,
            self.base_rpc_url,
            self.arbitrum_rpc_url,
            self.ethereum_indexed_rpc_url,
            self.base_indexed_rpc_url,
            self.arbitrum_indexed_rpc_url,
        )
        if not any(endpoint and endpoint.strip() for endpoint in wallet_rpc_endpoints) and not (
            self.alchemy_api_key and self.alchemy_api_key.strip()
        ):
            problems.append(
                "Configure at least one public wallet RPC endpoint, indexed EVM RPC endpoint, "
                "or ALCHEMY_API_KEY"
            )
        origin = urlparse(self.web_origin)
        if (
            origin.scheme != "https"
            or not origin.netloc
            or origin.path != ""
            or origin.query
            or origin.fragment
            or origin.username
            or origin.password
        ):
            problems.append("WEB_ORIGIN must be one HTTPS origin")
        endpoint_settings = (
            ("SOLANA_RPC_URL", self.solana_rpc_url),
            ("SOLANA_RPC_FALLBACK_URL", self.solana_rpc_fallback_url),
            ("EVM_RPC_URL", self.evm_rpc_url),
            ("ETHEREUM_RPC_URL", self.ethereum_rpc_url),
            ("BASE_RPC_URL", self.base_rpc_url),
            ("ARBITRUM_RPC_URL", self.arbitrum_rpc_url),
            ("ETHEREUM_INDEXED_RPC_URL", self.ethereum_indexed_rpc_url),
            ("BASE_INDEXED_RPC_URL", self.base_indexed_rpc_url),
            ("ARBITRUM_INDEXED_RPC_URL", self.arbitrum_indexed_rpc_url),
        )
        for setting_name, endpoint in endpoint_settings:
            if not endpoint or not endpoint.strip():
                continue
            try:
                parsed_endpoint = urlparse(endpoint.strip())
                is_secure_endpoint = (
                    parsed_endpoint.scheme == "https"
                    and parsed_endpoint.hostname is not None
                    and parsed_endpoint.username is None
                    and parsed_endpoint.password is None
                    and not parsed_endpoint.fragment
                )
            except ValueError:
                is_secure_endpoint = False
            if not is_secure_endpoint:
                problems.append(
                    f"{setting_name} must be a valid HTTPS endpoint without URL credentials"
                )

        try:
            price_endpoint = urlparse(self.coingecko_api_base_url.strip())
            is_secure_price_endpoint = (
                price_endpoint.scheme == "https"
                and price_endpoint.hostname is not None
                and price_endpoint.username is None
                and price_endpoint.password is None
                and not price_endpoint.query
                and not price_endpoint.fragment
            )
        except ValueError:
            is_secure_price_endpoint = False
        if not is_secure_price_endpoint:
            problems.append(
                "COINGECKO_API_BASE_URL must be an HTTPS endpoint without URL credentials"
            )
        for proxy_cidr in self.trusted_proxy_cidrs.split(","):
            if proxy_cidr.strip():
                try:
                    ipaddress.ip_network(proxy_cidr.strip(), strict=False)
                except ValueError:
                    problems.append("TRUSTED_PROXY_CIDRS must contain valid IP networks")
                    break

        if problems:
            raise RuntimeError("Invalid production configuration: " + "; ".join(problems))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
