from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ValuationSnapshot(Base):
    __tablename__ = "valuation_snapshots"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    portfolio_id: Mapped[UUID] = mapped_column(ForeignKey("portfolios.id"), index=True)
    total_value: Mapped[Decimal | None] = mapped_column(Numeric(28, 10), nullable=True)
    known_value: Mapped[Decimal] = mapped_column(Numeric(28, 10), default=Decimal("0"))
    reporting_currency: Mapped[str] = mapped_column(String(3))
    quality_status: Mapped[str] = mapped_column(String(32), default="fresh")
    calculation_version: Mapped[int] = mapped_column(default=2)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
