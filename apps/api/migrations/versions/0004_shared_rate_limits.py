"""Add shared API rate-limit counters."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_shared_rate_limits"
down_revision: str | Sequence[str] | None = "0003_wallet_import_history"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "rate_limit_windows",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("bucket_hash", sa.String(length=64), nullable=False),
        sa.Column("window_start", sa.BigInteger(), nullable=False),
        sa.Column("hit_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bucket_hash", "window_start", name="uq_rate_limit_bucket_window"),
    )
    op.create_index(
        "ix_rate_limit_windows_window_start", "rate_limit_windows", ["window_start"]
    )


def downgrade() -> None:
    op.drop_index("ix_rate_limit_windows_window_start", table_name="rate_limit_windows")
    op.drop_table("rate_limit_windows")
