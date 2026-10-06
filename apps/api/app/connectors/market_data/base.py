from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import httpx

from app.connectors.base import NormalizedBalance
from app.connectors.blockchain.networks import NetworkConfig
from app.schemas.common import QualityStatus


@dataclass(frozen=True)
class MarketPrice:
    amount: Decimal
    source_name: str
    retrieved_at: datetime
    provider_updated_at: datetime | None
    quality: QualityStatus


@dataclass(frozen=True)
class MarketPriceBatch:
    quotes: dict[str, MarketPrice]
    warnings: tuple[str, ...] = ()


class MarketDataConnector(ABC):
    @abstractmethod
    async def get_prices(
        self,
        balances: list[NormalizedBalance],
        network: NetworkConfig,
        quote_currency: str,
        client: httpx.AsyncClient,
    ) -> MarketPriceBatch:
        raise NotImplementedError
