from datetime import datetime
from typing import Literal

from pydantic import Field, ValidationInfo, field_validator

from app.schemas.common import APIModel, QualityStatus
from app.schemas.wallet import EVM_ADDRESS_PATTERN, NetworkId, _is_solana_public_key


class SourceRead(APIModel):
    id: str
    name: str
    kind: Literal["wallet", "exchange_import", "exchange_balance_import", "exchange_api", "demo"]
    network: str | None = None
    address_label: str | None = None
    last_updated_at: datetime | str | None = None
    quality: QualityStatus
    coverage: str | None = None
    warnings: list[str] = Field(default_factory=list)


class WalletSourceCreate(APIModel):
    name: str = Field(default="Public wallet", min_length=1, max_length=160)
    network: NetworkId
    address: str = Field(min_length=1, max_length=64)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Give this wallet a name.")
        return normalized

    @field_validator("address")
    @classmethod
    def normalize_address(cls, value: str, info: ValidationInfo) -> str:
        value = value.strip()
        network = info.data.get("network")
        if network == "solana" and not _is_solana_public_key(value):
            raise ValueError("Enter a valid Solana public address.")
        if network in {"ethereum", "base", "arbitrum"} and not EVM_ADDRESS_PATTERN.fullmatch(value):
            raise ValueError("Enter a valid EVM public address, starting with 0x.")
        if network in {"ethereum", "base", "arbitrum"}:
            value = value.lower()
        return value


class PersistedWalletSyncRead(APIModel):
    source: SourceRead
    snapshot: dict[str, object]
