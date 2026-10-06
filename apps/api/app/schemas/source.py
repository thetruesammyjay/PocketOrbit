from datetime import datetime
from typing import Literal

from app.schemas.common import APIModel, QualityStatus


class SourceRead(APIModel):
    id: str
    name: str
    kind: Literal["wallet", "exchange_import", "exchange_api", "demo"]
    network: str | None = None
    address_label: str | None = None
    last_updated_at: datetime | str | None = None
    quality: QualityStatus
