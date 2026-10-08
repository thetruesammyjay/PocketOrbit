from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Source(Base):
    __tablename__ = "portfolio_sources"
    __table_args__ = (
        Index(
            "uq_portfolio_wallet_address",
            "portfolio_id",
            "network_id",
            "public_address",
            unique=True,
            postgresql_where=text("kind = 'wallet' AND public_address IS NOT NULL"),
            sqlite_where=text("kind = 'wallet' AND public_address IS NOT NULL"),
        ),
        Index(
            "uq_portfolio_balance_source_name",
            "portfolio_id",
            func.lower(text("name")),
            unique=True,
            postgresql_where=text("kind = 'exchange_balance_import'"),
            sqlite_where=text("kind = 'exchange_balance_import'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    portfolio_id: Mapped[UUID] = mapped_column(ForeignKey("portfolios.id"), index=True)
    kind: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(160))
    network_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    public_address: Mapped[str | None] = mapped_column(String(256), nullable=True)
    quality_status: Mapped[str] = mapped_column(String(32), default="fresh")
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
