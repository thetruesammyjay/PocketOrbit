"""Preserve provider update times and price quality."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_price_provenance"
down_revision: str | Sequence[str] | None = "0006_valuation_calculation_version"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "prices",
        sa.Column("provider_updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "prices",
        sa.Column("quality_status", sa.String(length=32), nullable=False, server_default="fresh"),
    )
    with op.batch_alter_table("prices") as batch_op:
        batch_op.alter_column(
            "quality_status",
            existing_type=sa.String(length=32),
            server_default=None,
        )


def downgrade() -> None:
    with op.batch_alter_table("prices") as batch_op:
        batch_op.drop_column("quality_status")
        batch_op.drop_column("provider_updated_at")
