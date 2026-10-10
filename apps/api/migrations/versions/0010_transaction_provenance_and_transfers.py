"""Add transaction provenance, import coverage, and transfer review records."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010_transaction_provenance"
down_revision: str | Sequence[str] | None = "0009_import_snapshot_ref"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.add_column(sa.Column("import_job_id", sa.Uuid(), nullable=True))
        batch_op.add_column(sa.Column("dedupe_key", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("external_record_id", sa.String(length=256), nullable=True))
        batch_op.add_column(sa.Column("transaction_hash", sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column("fee_asset_id", sa.Uuid(), nullable=True))
        batch_op.add_column(sa.Column("quote_amount", sa.Numeric(38, 18), nullable=True))
        batch_op.add_column(sa.Column("quote_currency", sa.String(length=3), nullable=True))
        batch_op.create_foreign_key(
            "fk_transactions_fee_asset_id_assets", "assets", ["fee_asset_id"], ["id"]
        )
        batch_op.create_foreign_key(
            "fk_transactions_import_job_id_import_jobs",
            "import_jobs",
            ["import_job_id"],
            ["id"],
            ondelete="CASCADE",
        )
    op.create_index(
        "uq_transactions_dedupe_key",
        "transactions",
        ["dedupe_key"],
        unique=True,
        postgresql_where=sa.text("dedupe_key IS NOT NULL"),
        sqlite_where=sa.text("dedupe_key IS NOT NULL"),
    )
    op.create_index("ix_transactions_transaction_hash", "transactions", ["transaction_hash"])

    with op.batch_alter_table("import_jobs") as batch_op:
        batch_op.add_column(
            sa.Column("rows_duplicate", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("coverage_start_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(sa.Column("coverage_end_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(
            sa.Column("history_complete", sa.Boolean(), nullable=False, server_default=sa.false())
        )

    op.execute(
        sa.text(
            "WITH ranked_sources AS (SELECT id, row_number() OVER ("
            "PARTITION BY portfolio_id, lower(name) ORDER BY created_at, id) AS source_rank "
            "FROM portfolio_sources WHERE kind = 'exchange_import') "
            "UPDATE portfolio_sources SET name = substr(name, 1, 140) || ' (legacy ' || "
            "substr(CAST(id AS VARCHAR), 1, 8) || ')' WHERE id IN ("
            "SELECT id FROM ranked_sources WHERE source_rank > 1)"
        )
    )
    op.create_index(
        "uq_portfolio_transaction_source_name",
        "portfolio_sources",
        ["portfolio_id", sa.text("lower(name)")],
        unique=True,
        postgresql_where=sa.text("kind = 'exchange_import'"),
        sqlite_where=sa.text("kind = 'exchange_import'"),
    )
    op.create_index("ix_transactions_import_job_id", "transactions", ["import_job_id"])

    op.create_table(
        "transfer_matches",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("portfolio_id", sa.Uuid(), nullable=False),
        sa.Column("outgoing_transaction_id", sa.Uuid(), nullable=False),
        sa.Column("incoming_transaction_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column("rationale", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["outgoing_transaction_id"], ["transactions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["incoming_transaction_id"], ["transactions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "outgoing_transaction_id", "incoming_transaction_id", name="uq_transfer_match_pair"
        ),
    )
    op.create_index("ix_transfer_matches_portfolio_id", "transfer_matches", ["portfolio_id"])
    op.create_index(
        "ix_transfer_matches_outgoing_transaction_id",
        "transfer_matches",
        ["outgoing_transaction_id"],
    )
    op.create_index(
        "ix_transfer_matches_incoming_transaction_id",
        "transfer_matches",
        ["incoming_transaction_id"],
    )
    op.create_index(
        "ix_transfer_matches_portfolio_status", "transfer_matches", ["portfolio_id", "status"]
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_import_job_id", table_name="transactions")
    op.drop_index("uq_portfolio_transaction_source_name", table_name="portfolio_sources")
    op.drop_index("ix_transfer_matches_portfolio_status", table_name="transfer_matches")
    op.drop_index("ix_transfer_matches_incoming_transaction_id", table_name="transfer_matches")
    op.drop_index("ix_transfer_matches_outgoing_transaction_id", table_name="transfer_matches")
    op.drop_index("ix_transfer_matches_portfolio_id", table_name="transfer_matches")
    op.drop_table("transfer_matches")
    with op.batch_alter_table("import_jobs") as batch_op:
        batch_op.drop_column("history_complete")
        batch_op.drop_column("coverage_end_at")
        batch_op.drop_column("coverage_start_at")
        batch_op.drop_column("rows_duplicate")
    op.drop_index("ix_transactions_transaction_hash", table_name="transactions")
    op.drop_index("uq_transactions_dedupe_key", table_name="transactions")
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.drop_constraint("fk_transactions_import_job_id_import_jobs", type_="foreignkey")
        batch_op.drop_constraint("fk_transactions_fee_asset_id_assets", type_="foreignkey")
        batch_op.drop_column("quote_currency")
        batch_op.drop_column("quote_amount")
        batch_op.drop_column("fee_asset_id")
        batch_op.drop_column("transaction_hash")
        batch_op.drop_column("dedupe_key")
        batch_op.drop_column("external_record_id")
        batch_op.drop_column("import_job_id")
