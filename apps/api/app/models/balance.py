from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Balance(Base):
    __tablename__ = "balances"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    source_id: Mapped[UUID] = mapped_column(ForeignKey("portfolio_sources.id"), index=True)
    snapshot_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("wallet_snapshots.id", ondelete="CASCADE"), nullable=True, index=True
    )
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("assets.id"), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(38, 18))
    quality_status: Mapped[str] = mapped_column(String(32), default="fresh")
    source_record_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
