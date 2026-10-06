from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Price(Base):
    __tablename__ = "prices"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("assets.id"), index=True)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    quote_currency: Mapped[str] = mapped_column(String(3), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(28, 10))
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
