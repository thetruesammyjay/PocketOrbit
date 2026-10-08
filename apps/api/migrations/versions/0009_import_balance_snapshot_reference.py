"""Link balance imports to their individual saved snapshots."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_import_snapshot_ref"
down_revision: str | Sequence[str] | None = "0008_portfolio_read_indexes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("import_jobs") as batch_op:
        batch_op.add_column(sa.Column("snapshot_id", sa.Uuid(), nullable=True))
        batch_op.create_foreign_key(
            "fk_import_jobs_snapshot_id_wallet_snapshots",
            "wallet_snapshots",
            ["snapshot_id"],
            ["id"],
            ondelete="SET NULL",
        )
    op.execute(
        sa.text(
            "UPDATE import_jobs SET snapshot_id = ("
            "SELECT wallet_snapshots.id FROM wallet_snapshots "
            "JOIN portfolio_sources ON portfolio_sources.id = wallet_snapshots.source_id "
            "WHERE wallet_snapshots.source_id = import_jobs.source_id "
            "AND portfolio_sources.kind = 'exchange_balance_import' "
            "ORDER BY wallet_snapshots.retrieved_at DESC, wallet_snapshots.id DESC LIMIT 1"
            ") WHERE import_jobs.snapshot_id IS NULL AND import_jobs.source_id IS NOT NULL"
        )
    )
    op.execute(
        sa.text(
            "WITH ranked_sources AS ("
            "SELECT id, row_number() OVER ("
            "PARTITION BY portfolio_id, lower(name) ORDER BY created_at, id"
            ") AS source_rank FROM portfolio_sources "
            "WHERE kind = 'exchange_balance_import'"
            ") UPDATE portfolio_sources SET name = "
            "substr(name, 1, 140) || ' (legacy ' || substr(CAST(id AS VARCHAR), 1, 8) || ')' "
            "WHERE id IN (SELECT id FROM ranked_sources WHERE source_rank > 1)"
        )
    )
    op.create_index("ix_import_jobs_snapshot_id", "import_jobs", ["snapshot_id"])
    op.create_index(
        "uq_portfolio_balance_source_name",
        "portfolio_sources",
        ["portfolio_id", sa.text("lower(name)")],
        unique=True,
        postgresql_where=sa.text("kind = 'exchange_balance_import'"),
        sqlite_where=sa.text("kind = 'exchange_balance_import'"),
    )


def downgrade() -> None:
    op.drop_index("uq_portfolio_balance_source_name", table_name="portfolio_sources")
    op.drop_index("ix_import_jobs_snapshot_id", table_name="import_jobs")
    with op.batch_alter_table("import_jobs") as batch_op:
        batch_op.drop_constraint(
            "fk_import_jobs_snapshot_id_wallet_snapshots", type_="foreignkey"
        )
        batch_op.drop_column("snapshot_id")
