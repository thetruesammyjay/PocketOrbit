from decimal import Decimal

from pydantic import Field

from app.schemas.activity import ActivityRead
from app.schemas.common import APIModel, QualityStatus
from app.schemas.source import SourceRead


class HoldingRead(APIModel):
    asset: dict[str, str | None]
    quantity: Decimal
    unit_price: Decimal
    value: Decimal
    change_24h: Decimal | None = None
    source_ids: list[str] = Field(default_factory=list)


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
    total_value: Decimal
    change_24h: Decimal
    change_percent_24h: Decimal
    calculated_at: str
    quality: QualityStatus
    holdings: list[HoldingRead]
    sources: list[SourceRead]
    allocation: list[AllocationRead]
    activity: list[ActivityRead]
    history: list[float]
