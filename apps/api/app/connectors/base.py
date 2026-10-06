from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import httpx


class ProviderNotConfiguredError(RuntimeError):
    """Raised when an optional third-party provider is not configured."""


class ProviderRequestError(RuntimeError):
    """Raised when a configured data provider cannot return a valid response."""


@dataclass(frozen=True)
class NormalizedBalance:
    asset_id: str
    symbol: str
    name: str
    network_id: str
    quantity: Decimal
    contract_address: str | None
    decimals: int
    source_record_ids: tuple[str, ...]
    retrieved_at: datetime
    block_reference: str | None = None


class BalanceConnector(ABC):
    @abstractmethod
    async def get_balances(
        self, public_address: str, client: httpx.AsyncClient
    ) -> list[NormalizedBalance]:
        raise NotImplementedError
