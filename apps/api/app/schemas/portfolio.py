import re
from datetime import datetime
from decimal import Decimal

from pydantic import Field, field_validator

from app.schemas.activity import ActivityRead
from app.schemas.common import APIModel, QualityStatus
from app.schemas.source import SourceRead


class HoldingProvenance(APIModel):
    balance_sources: list[str] = Field(default_factory=list)
    balance_retrieved_at: datetime | None = None
    price_provider: str | None = None
    price_retrieved_at: datetime | None = None
    price_provider_updated_at: datetime | None = None
    quality: QualityStatus


class HoldingRead(APIModel):
    """A normalized asset position with its source and price trail."""

    asset: dict[str, str | None]
    quantity: Decimal
    unit_price: Decimal | None = None
    value: Decimal | None = None
    change_24h: Decimal | None = None
    source_ids: list[str] = Field(default_factory=list)
    provenance: HoldingProvenance


class AllocationRead(APIModel):
    name: str
    value: Decimal
    percentage: Decimal
    color: str


class PortfolioSummaryRead(APIModel):
    id: str
    name: str
    is_demo: bool
    reporting_currency: str
    total_value: Decimal | None = None
    known_value: Decimal
    change_24h: Decimal | None = None
    change_percent_24h: Decimal | None = None
    calculated_at: str
    quality: QualityStatus
    warnings: list[str] = Field(default_factory=list)
    holdings: list[HoldingRead]
    sources: list[SourceRead]
    allocation: list[AllocationRead]
    activity: list[ActivityRead]
    history: list[float]


class PortfolioCreate(APIModel):
    name: str = Field(default="My portfolio", min_length=1, max_length=120)
    reporting_currency: str = Field(default="USD", min_length=3, max_length=3)

    @field_validator("reporting_currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not re.fullmatch(r"[A-Z]{3}", normalized):
            raise ValueError("Use a three-letter reporting currency such as USD.")
        return normalized


class PortfolioRead(APIModel):
    id: str
    name: str
    reporting_currency: str
    created_at: str
