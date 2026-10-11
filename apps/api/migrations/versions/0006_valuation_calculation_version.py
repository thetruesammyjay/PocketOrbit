"""Version valuations and retain the start of imported activity history."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_valuation_calculation_version"
down_revision: str | Sequence[str] | None = "0005_email_verification_recovery"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Alembic creates this column as VARCHAR(32), but this revision ID is longer.
    # Widen it before Alembic records the new revision after this upgrade runs.
    op.alter_column(
        "alembic_version",
        "version_num",
        existing_type=sa.String(length=32),
        type_=sa.String(length=64),
        existing_nullable=False,
    )
    op.add_column(
        "valuation_snapshots",
        sa.Column("calculation_version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "portfolios",
        sa.Column("import_history_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        sa.text(
            "UPDATE portfolios SET import_history_started_at = "
            "(SELECT MIN(portfolio_sources.created_at) FROM portfolio_sources "
            "WHERE portfolio_sources.portfolio_id = portfolios.id "
            "AND portfolio_sources.kind = 'exchange_import') "
            "WHERE EXISTS (SELECT 1 FROM portfolio_sources "
            "WHERE portfolio_sources.portfolio_id = portfolios.id "
            "AND portfolio_sources.kind = 'exchange_import')"
        )
    )


def downgrade() -> None:
    op.drop_column("portfolios", "import_history_started_at")
    op.drop_column("valuation_snapshots", "calculation_version")
