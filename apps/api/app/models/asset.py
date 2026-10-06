from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    canonical_id: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(160))
    network_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    contract_address: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    decimals: Mapped[int] = mapped_column(default=18)


class AssetMapping(Base):
    __tablename__ = "asset_mappings"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("assets.id"), index=True)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    provider_asset_id: Mapped[str] = mapped_column(String(256), index=True)
    match_confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), default=Decimal("1.0"))
