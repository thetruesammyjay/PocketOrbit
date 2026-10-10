from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ImportJob(Base):
    __tablename__ = "import_jobs"
    __table_args__ = (
        Index(
            "uq_import_jobs_portfolio_file_hash",
            "portfolio_id",
            "file_sha256",
            unique=True,
            postgresql_where=text("file_sha256 IS NOT NULL"),
            sqlite_where=text("file_sha256 IS NOT NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    portfolio_id: Mapped[UUID] = mapped_column(ForeignKey("portfolios.id"), index=True)
    source_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("portfolio_sources.id", ondelete="SET NULL"), nullable=True, index=True
    )
    snapshot_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("wallet_snapshots.id", ondelete="SET NULL"), nullable=True, index=True
    )
    filename: Mapped[str] = mapped_column(String(255))
    file_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="received")
    rows_received: Mapped[int] = mapped_column(Integer, default=0)
    rows_accepted: Mapped[int] = mapped_column(Integer, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0)
    rows_duplicate: Mapped[int] = mapped_column(Integer, default=0)
    coverage_start_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    coverage_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    history_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
