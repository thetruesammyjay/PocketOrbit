from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation

import httpx

from app.connectors.base import (
    NormalizedBalance,
    ProviderNotConfiguredError,
    ProviderRequestError,
)
from app.connectors.blockchain.networks import NetworkConfig
from app.connectors.market_data.base import MarketDataConnector, MarketPrice, MarketPriceBatch
from app.core.config import settings
from app.schemas.common import QualityStatus

PROVIDER_NAME = "CoinGecko"
PRICE_MAX_AGE = timedelta(minutes=10)


def _quote(entry: object, currency: str, retrieved_at: datetime) -> MarketPrice | None:
    if not isinstance(entry, dict):
        return None
    raw_amount = entry.get(currency.lower())
    if raw_amount is None:
        return None
    try:
        amount = Decimal(str(raw_amount))
    except (InvalidOperation, ValueError):
        return None
    if not amount.is_finite() or amount < 0:
        return None

    updated_at: datetime | None = None
    raw_timestamp = entry.get("last_updated_at")
    if isinstance(raw_timestamp, (int, float)):
        try:
            updated_at = datetime.fromtimestamp(raw_timestamp, UTC)
        except (OverflowError, OSError, ValueError):
            updated_at = None
    if updated_at is None:
        quality = QualityStatus.ESTIMATED
    elif retrieved_at - updated_at > PRICE_MAX_AGE:
        quality = QualityStatus.DELAYED
    else:
        quality = QualityStatus.FRESH
    return MarketPrice(
        amount=amount,
        source_name=PROVIDER_NAME,
        retrieved_at=retrieved_at,
        provider_updated_at=updated_at,
        quality=quality,
    )


class CoinGeckoConnector(MarketDataConnector):
    async def _get_json(
        self,
        client: httpx.AsyncClient,
        path: str,
        params: dict[str, str],
    ) -> dict[str, object]:
        api_key = (settings.coingecko_api_key or "").strip()
        if not api_key:
            raise ProviderNotConfiguredError("CoinGecko pricing is not configured.")
        if settings.coingecko_api_key_header not in {
            "x-cg-demo-api-key",
            "x-cg-pro-api-key",
        }:
            raise ProviderNotConfiguredError("The configured CoinGecko API key type is not supported.")

        headers = {settings.coingecko_api_key_header: api_key}
        url = f"{settings.coingecko_api_base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            response = await client.get(url, params=params, headers=headers)
            if response.status_code == 429:
                raise ProviderRequestError("CoinGecko rate-limited the price request.")
            response.raise_for_status()
            payload = response.json()
        except ProviderRequestError:
            raise
        except (httpx.HTTPError, ValueError) as exc:
            # Do not include exception text; request headers contain the provider key.
            raise ProviderRequestError("CoinGecko could not return a price response.") from exc
        if not isinstance(payload, dict):
            raise ProviderRequestError("CoinGecko returned an invalid price response.")
        return payload

    async def get_prices(
        self,
        balances: list[NormalizedBalance],
        network: NetworkConfig,
        quote_currency: str,
        client: httpx.AsyncClient,
    ) -> MarketPriceBatch:
        if not (settings.coingecko_api_key or "").strip():
            return MarketPriceBatch(
                {}, ("Market prices are unavailable until a CoinGecko API key is configured.",)
            )

        currency = quote_currency.lower()
        warnings: list[str] = []
        quotes: dict[str, MarketPrice] = {}
        try:
            native_payload = await self._get_json(
                client,
                "simple/price",
                {
                    "ids": network.native_price_id,
                    "vs_currencies": currency,
                    "include_last_updated_at": "true",
                },
            )
            native_retrieved_at = datetime.now(UTC)
            native_quote = _quote(native_payload.get(network.native_price_id), currency, native_retrieved_at)
            if native_quote:
                for balance in balances:
                    if balance.contract_address is None:
                        quotes[balance.asset_id] = native_quote
        except (ProviderNotConfiguredError, ProviderRequestError):
            warnings.append("The native asset price could not be retrieved.")

        token_balances = [balance for balance in balances if balance.contract_address]
        if token_balances:
            addresses = sorted(
                {
                    balance.contract_address.lower()
                    for balance in token_balances
                    if balance.contract_address
                }
            )
            for start in range(0, len(addresses), 100):
                address_batch = addresses[start : start + 100]
                try:
                    token_payload = await self._get_json(
                        client,
                        f"simple/token_price/{network.price_platform_id}",
                        {
                            "contract_addresses": ",".join(address_batch),
                            "vs_currencies": currency,
                            "include_last_updated_at": "true",
                        },
                    )
                except (ProviderNotConfiguredError, ProviderRequestError):
                    warnings.append("One or more token prices could not be retrieved.")
                    break
                token_retrieved_at = datetime.now(UTC)
                for balance in token_balances:
                    if (
                        not balance.contract_address
                        or balance.contract_address.lower() not in address_batch
                    ):
                        continue
                    token_quote = _quote(
                        token_payload.get(balance.contract_address.lower()),
                        currency,
                        token_retrieved_at,
                    )
                    if token_quote:
                        quotes[balance.asset_id] = token_quote

        return MarketPriceBatch(quotes=quotes, warnings=tuple(warnings))
