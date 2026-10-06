import httpx

from app.connectors.base import NormalizedBalance
from app.connectors.blockchain.networks import NetworkConfig
from app.connectors.market_data.base import MarketPrice as PriceQuote
from app.connectors.market_data.base import MarketPriceBatch as PriceResolution
from app.connectors.market_data.coingecko import CoinGeckoConnector

__all__ = ["PriceQuote", "PriceResolution", "resolve_prices"]


async def resolve_prices(
    balances: list[NormalizedBalance],
    network: NetworkConfig,
    quote_currency: str,
    client: httpx.AsyncClient,
) -> PriceResolution:
    return await CoinGeckoConnector().get_prices(
        balances=balances,
        network=network,
        quote_currency=quote_currency,
        client=client,
    )
