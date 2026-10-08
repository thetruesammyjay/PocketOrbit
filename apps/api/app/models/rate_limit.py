from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Index, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RateLimitWindow(Base):
    """A shared fixed-window counter with no raw IP or account identifiers."""

    __tablename__ = "rate_limit_windows"
    __table_args__ = (
        UniqueConstraint("bucket_hash", "window_start", name="uq_rate_limit_bucket_window"),
        Index("ix_rate_limit_windows_window_start", "window_start"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    bucket_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    window_start: Mapped[int] = mapped_column(BigInteger, nullable=False)
    hit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
