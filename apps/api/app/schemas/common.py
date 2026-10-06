from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class QualityStatus(StrEnum):
    FRESH = "fresh"
    DELAYED = "delayed"
    PARTIAL = "partial"
    NEEDS_REVIEW = "needs_review"
    UNMATCHED = "unmatched"
    OFFLINE = "offline"
    ESTIMATED = "estimated"


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class Provenance(APIModel):
    source_name: str
    price_provider: str | None = None
    retrieved_at: datetime | None = None
    calculated_at: datetime | None = None
    quality: QualityStatus
