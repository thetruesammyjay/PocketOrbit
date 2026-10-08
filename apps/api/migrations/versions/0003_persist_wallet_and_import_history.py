"""Persist wallet balance snapshots and import provenance."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_wallet_import_history"
down_revision: str | Sequence[str] | None = "0002_auth_sessions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "wallet_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("quote_currency", sa.String(length=3), nullable=False),
        sa.Column("known_value", sa.Numeric(precision=28, scale=10), nullable=False),
        sa.Column("total_value", sa.Numeric(precision=28, scale=10), nullable=True),
        sa.Column("quality_status", sa.String(length=32), nullable=False),
        sa.Column("coverage", sa.String(length=96), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["portfolio_sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_wallet_snapshots_source_id", "wallet_snapshots", ["source_id"])
    op.create_index("ix_wallet_snapshots_retrieved_at", "wallet_snapshots", ["retrieved_at"])

    with op.batch_alter_table("balances") as batch_op:
        batch_op.add_column(sa.Column("snapshot_id", sa.Uuid(), nullable=True))
        batch_op.create_foreign_key(
            "fk_balances_snapshot_id_wallet_snapshots",
            "wallet_snapshots",
            ["snapshot_id"],
            ["id"],
            ondelete="CASCADE",
        )
    op.create_index("ix_balances_snapshot_id", "balances", ["snapshot_id"])

    with op.batch_alter_table("import_jobs") as batch_op:
        batch_op.add_column(sa.Column("source_id", sa.Uuid(), nullable=True))
        batch_op.add_column(sa.Column("file_sha256", sa.String(length=64), nullable=True))
        batch_op.create_foreign_key(
            "fk_import_jobs_source_id_portfolio_sources",
            "portfolio_sources",
            ["source_id"],
            ["id"],
            ondelete="SET NULL",
        )
    op.create_index("ix_import_jobs_source_id", "import_jobs", ["source_id"])
    op.create_index("ix_import_jobs_file_sha256", "import_jobs", ["file_sha256"])
    op.create_index(
        "uq_import_jobs_portfolio_file_hash",
        "import_jobs",
        ["portfolio_id", "file_sha256"],
        unique=True,
        postgresql_where=sa.text("file_sha256 IS NOT NULL"),
        sqlite_where=sa.text("file_sha256 IS NOT NULL"),
    )
    op.create_index(
        "uq_transactions_source_record",
        "transactions",
        ["source_id", "source_record_id"],
        unique=True,
        postgresql_where=sa.text("source_record_id IS NOT NULL"),
        sqlite_where=sa.text("source_record_id IS NOT NULL"),
    )
    op.create_index(
        "uq_portfolio_wallet_address",
        "portfolio_sources",
        ["portfolio_id", "network_id", "public_address"],
        unique=True,
        postgresql_where=sa.text("kind = 'wallet' AND public_address IS NOT NULL"),
        sqlite_where=sa.text("kind = 'wallet' AND public_address IS NOT NULL"),
    )

    with op.batch_alter_table("valuation_snapshots") as batch_op:
        batch_op.alter_column(
            "total_value",
            existing_type=sa.Numeric(precision=28, scale=10),
            nullable=True,
        )
        batch_op.add_column(
            sa.Column(
                "known_value",
                sa.Numeric(precision=28, scale=10),
                nullable=False,
                server_default="0",
            )
        )
    with op.batch_alter_table("valuation_snapshots") as batch_op:
        batch_op.alter_column(
            "known_value",
            existing_type=sa.Numeric(precision=28, scale=10),
            server_default=None,
        )


def downgrade() -> None:
    op.drop_index("uq_portfolio_wallet_address", table_name="portfolio_sources")
    op.drop_index("uq_transactions_source_record", table_name="transactions")
    op.drop_index("uq_import_jobs_portfolio_file_hash", table_name="import_jobs")
    with op.batch_alter_table("valuation_snapshots") as batch_op:
        batch_op.drop_column("known_value")
        batch_op.alter_column(
            "total_value",
            existing_type=sa.Numeric(precision=28, scale=10),
            nullable=False,
        )
    op.drop_index("ix_import_jobs_file_sha256", table_name="import_jobs")
    op.drop_index("ix_import_jobs_source_id", table_name="import_jobs")
    with op.batch_alter_table("import_jobs") as batch_op:
        batch_op.drop_constraint("fk_import_jobs_source_id_portfolio_sources", type_="foreignkey")
        batch_op.drop_column("file_sha256")
        batch_op.drop_column("source_id")
    op.drop_index("ix_balances_snapshot_id", table_name="balances")
    with op.batch_alter_table("balances") as batch_op:
        batch_op.drop_constraint("fk_balances_snapshot_id_wallet_snapshots", type_="foreignkey")
        batch_op.drop_column("snapshot_id")
    op.drop_index("ix_wallet_snapshots_retrieved_at", table_name="wallet_snapshots")
    op.drop_index("ix_wallet_snapshots_source_id", table_name="wallet_snapshots")
    op.drop_table("wallet_snapshots")
