from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import httpx


class ProviderNotConfiguredError(RuntimeError):
    """Raised when an optional third-party provider is not configured."""


class ProviderRequestError(RuntimeError):
    """Raised when a configured data provider cannot return a valid response."""


def decimal_from_base_units(amount: int, decimals: int) -> Decimal:
    """Convert an integer token amount exactly, without applying Decimal context rounding."""
    if isinstance(decimals, bool) or not isinstance(decimals, int) or not 0 <= decimals <= 255:
        raise ValueError("Token decimals must be between 0 and 255.")
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("A base-unit amount must be an integer.")
    digits = tuple(int(digit) for digit in str(abs(amount)))
    return Decimal((1 if amount < 0 else 0, digits, -decimals))


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
