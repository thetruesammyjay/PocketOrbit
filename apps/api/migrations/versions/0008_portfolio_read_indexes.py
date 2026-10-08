"""Index newest snapshot, price, and activity reads."""

from collections.abc import Sequence

from alembic import op

revision: str = "0008_portfolio_read_indexes"
down_revision: str | Sequence[str] | None = "0007_price_provenance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_wallet_snapshots_source_retrieved_at",
        "wallet_snapshots",
        ["source_id", "retrieved_at", "id"],
    )
    op.create_index(
        "ix_prices_asset_currency_retrieved_at",
        "prices",
        ["asset_id", "quote_currency", "retrieved_at", "id"],
    )
    op.create_index(
        "ix_transactions_source_occurred_at",
        "transactions",
        ["source_id", "occurred_at", "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_source_occurred_at", table_name="transactions")
    op.drop_index("ix_prices_asset_currency_retrieved_at", table_name="prices")
    op.drop_index("ix_wallet_snapshots_source_retrieved_at", table_name="wallet_snapshots")
