from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (
        Index(
            "ix_prices_asset_currency_retrieved_at",
            "asset_id",
            "quote_currency",
            "retrieved_at",
            "id",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("assets.id"), index=True)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    quote_currency: Mapped[str] = mapped_column(String(3), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(28, 10))
    provider_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    quality_status: Mapped[str] = mapped_column(String(32), default="fresh")
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
