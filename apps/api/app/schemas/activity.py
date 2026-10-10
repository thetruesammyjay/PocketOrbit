from datetime import datetime
from decimal import Decimal
from typing import Literal

from app.schemas.common import APIModel


class ActivityRead(APIModel):
    id: str
    kind: str
    asset_symbol: str
    quantity: Decimal
    source_name: str
    occurred_at: datetime | str
    status: Literal["confirmed", "pending", "needs_review", "user_confirmed", "rejected"]
    transaction_hash: str | None = None
    external_record_id: str | None = None
    quote_amount: Decimal | None = None
    quote_currency: str | None = None
    transfer_status: Literal["suggested", "matched", "rejected"] | None = None
