import re
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator
from pydantic.alias_generators import to_camel

from app.schemas.common import QualityStatus

SOLANA_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
EVM_ADDRESS_PATTERN = re.compile(r"^0x[0-9a-fA-F]{40}$")
NetworkId = Literal["solana", "ethereum", "base", "arbitrum"]


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


def _is_solana_public_key(value: str) -> bool:
    if not value or any(character not in SOLANA_ALPHABET for character in value):
        return False
    number = 0
    for character in value:
        number = number * 58 + SOLANA_ALPHABET.index(character)
    leading_zeroes = len(value) - len(value.lstrip("1"))
    decoded = (b"\x00" * leading_zeroes) + (
        number.to_bytes((number.bit_length() + 7) // 8, "big") if number else b""
    )
    return len(decoded) == 32


class WalletSyncRequest(CamelModel):
    network: NetworkId
    address: str = Field(min_length=1, max_length=64)
    quote_currency: str = Field(default="USD", min_length=3, max_length=5)

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str, info: ValidationInfo) -> str:
        value = value.strip()
        network = info.data.get("network")
        if network == "solana" and not _is_solana_public_key(value):
            raise ValueError("Enter a valid Solana public address.")
        if network in {"ethereum", "base", "arbitrum"} and not EVM_ADDRESS_PATTERN.fullmatch(value):
            raise ValueError("Enter a valid EVM public address, starting with 0x.")
        return value

    @field_validator("quote_currency")
    @classmethod
    def normalize_quote_currency(cls, value: str) -> str:
        value = value.strip().upper()
        if not value.isalpha():
            raise ValueError("Use a supported three-letter quote currency such as USD.")
        return value


class PriceProvenance(CamelModel):
    source_name: str
    retrieved_at: datetime
    provider_updated_at: datetime | None = None
    quality: QualityStatus


class BalanceProvenance(CamelModel):
    source_name: str
    source_record_ids: list[str] = Field(default_factory=list)
    retrieved_at: datetime
    block_reference: str | None = None


class LiveWalletBalance(CamelModel):
    asset_id: str
    symbol: str
    name: str
    network: str
    contract_address: str | None = None
    quantity: Decimal
    decimals: int
    quote_currency: str
    unit_price: Decimal | None = None
    value: Decimal | None = None
    quality: QualityStatus
    balance_provenance: BalanceProvenance
    price_provenance: PriceProvenance | None = None


class WalletSyncResponse(CamelModel):
    network: str
    network_name: str
    coverage: Literal[
        "not_synced",
        "native_and_spl_token2022_fungible_balances",
        "native_and_configured_erc20_balances",
        "native_and_indexed_erc20_balances",
    ]
    address: str
    is_live: bool = True
    is_persisted: bool = False
    source_id: str | None = None
    snapshot_id: str | None = None
    retrieved_at: datetime
    quote_currency: str
    total_value: Decimal | None = None
    known_value: Decimal
    quality: QualityStatus
    balances: list[LiveWalletBalance]
    warnings: list[str] = Field(default_factory=list)
