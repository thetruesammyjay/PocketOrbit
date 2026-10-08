from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index(
            "uq_transactions_source_record",
            "source_id",
            "source_record_id",
            unique=True,
            postgresql_where=text("source_record_id IS NOT NULL"),
            sqlite_where=text("source_record_id IS NOT NULL"),
        ),
        Index("ix_transactions_source_occurred_at", "source_id", "occurred_at", "id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    source_id: Mapped[UUID] = mapped_column(ForeignKey("portfolio_sources.id"), index=True)
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("assets.id"), index=True)
    source_record_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    kind: Mapped[str] = mapped_column(String(32), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(38, 18))
    fee_quantity: Mapped[Decimal | None] = mapped_column(Numeric(38, 18), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    quality_status: Mapped[str] = mapped_column(String(32), default="fresh")
