from datetime import datetime
from decimal import Decimal
from typing import Literal

from app.schemas.common import APIModel


class ActivityRead(APIModel):
    id: str
    kind: Literal["received", "sent", "trade", "fee", "deposit", "withdrawal"]
    asset_symbol: str
    quantity: Decimal
    source_name: str
    occurred_at: datetime | str
    status: Literal["confirmed", "pending", "needs_review"]
