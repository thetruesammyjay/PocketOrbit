from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WalletSnapshot(Base):
    __tablename__ = "wallet_snapshots"
    __table_args__ = (
        Index("ix_wallet_snapshots_source_retrieved_at", "source_id", "retrieved_at", "id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("portfolio_sources.id", ondelete="CASCADE"), index=True
    )
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    quote_currency: Mapped[str] = mapped_column(String(3))
    known_value: Mapped[Decimal] = mapped_column(Numeric(28, 10))
    total_value: Mapped[Decimal | None] = mapped_column(Numeric(28, 10), nullable=True)
    quality_status: Mapped[str] = mapped_column(String(32), default="fresh")
    coverage: Mapped[str] = mapped_column(String(96))
    warnings: Mapped[list[str]] = mapped_column(JSON, default=list)
