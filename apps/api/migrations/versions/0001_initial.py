"""Create the initial PocketOrbit persistence schema."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "portfolios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("reporting_currency", sa.String(length=3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_portfolios_user_id", "portfolios", ["user_id"])

    op.create_table(
        "assets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("canonical_id", sa.String(length=160), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("network_id", sa.String(length=64), nullable=True),
        sa.Column("contract_address", sa.String(length=256), nullable=True),
        sa.Column("decimals", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assets_canonical_id", "assets", ["canonical_id"], unique=True)
    op.create_index("ix_assets_symbol", "assets", ["symbol"])
    op.create_index("ix_assets_network_id", "assets", ["network_id"])
    op.create_index("ix_assets_contract_address", "assets", ["contract_address"])

    op.create_table(
        "portfolio_sources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("portfolio_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("network_id", sa.String(length=64), nullable=True),
        sa.Column("public_address", sa.String(length=256), nullable=True),
        sa.Column("quality_status", sa.String(length=32), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_portfolio_sources_portfolio_id", "portfolio_sources", ["portfolio_id"])
    op.create_index("ix_portfolio_sources_kind", "portfolio_sources", ["kind"])

    op.create_table(
        "asset_mappings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("asset_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("provider_asset_id", sa.String(length=256), nullable=False),
        sa.Column("match_confidence", sa.Numeric(precision=4, scale=3), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_asset_mappings_asset_id", "asset_mappings", ["asset_id"])
    op.create_index("ix_asset_mappings_provider", "asset_mappings", ["provider"])
    op.create_index("ix_asset_mappings_provider_asset_id", "asset_mappings", ["provider_asset_id"])

    op.create_table(
        "balances",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("asset_id", sa.Uuid(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=38, scale=18), nullable=False),
        sa.Column("quality_status", sa.String(length=32), nullable=False),
        sa.Column("source_record_id", sa.String(length=256), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["portfolio_sources.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_balances_source_id", "balances", ["source_id"])
    op.create_index("ix_balances_asset_id", "balances", ["asset_id"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("asset_id", sa.Uuid(), nullable=False),
        sa.Column("source_record_id", sa.String(length=256), nullable=True),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=38, scale=18), nullable=False),
        sa.Column("fee_quantity", sa.Numeric(precision=38, scale=18), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("quality_status", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["portfolio_sources.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_source_id", "transactions", ["source_id"])
    op.create_index("ix_transactions_asset_id", "transactions", ["asset_id"])
    op.create_index("ix_transactions_kind", "transactions", ["kind"])
    op.create_index("ix_transactions_occurred_at", "transactions", ["occurred_at"])

    op.create_table(
        "prices",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("asset_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("quote_currency", sa.String(length=3), nullable=False),
        sa.Column("price", sa.Numeric(precision=28, scale=10), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_prices_asset_id", "prices", ["asset_id"])
    op.create_index("ix_prices_provider", "prices", ["provider"])
    op.create_index("ix_prices_quote_currency", "prices", ["quote_currency"])
    op.create_index("ix_prices_retrieved_at", "prices", ["retrieved_at"])

    op.create_table(
        "valuation_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("portfolio_id", sa.Uuid(), nullable=False),
        sa.Column("total_value", sa.Numeric(precision=28, scale=10), nullable=False),
        sa.Column("reporting_currency", sa.String(length=3), nullable=False),
        sa.Column("quality_status", sa.String(length=32), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_valuation_snapshots_portfolio_id", "valuation_snapshots", ["portfolio_id"])
    op.create_index(
        "ix_valuation_snapshots_calculated_at", "valuation_snapshots", ["calculated_at"]
    )

    op.create_table(
        "import_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("portfolio_id", sa.Uuid(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("rows_received", sa.Integer(), nullable=False),
        sa.Column("rows_accepted", sa.Integer(), nullable=False),
        sa.Column("rows_rejected", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_import_jobs_portfolio_id", "import_jobs", ["portfolio_id"])

    op.create_table(
        "sync_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("message", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["portfolio_sources.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sync_jobs_source_id", "sync_jobs", ["source_id"])

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=True),
        sa.Column("target_id", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_events_actor_id", "audit_events", ["actor_id"])
    op.create_index("ix_audit_events_action", "audit_events", ["action"])
    op.create_index("ix_audit_events_created_at", "audit_events", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_audit_events_created_at", table_name="audit_events")
    op.drop_index("ix_audit_events_action", table_name="audit_events")
    op.drop_index("ix_audit_events_actor_id", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_sync_jobs_source_id", table_name="sync_jobs")
    op.drop_table("sync_jobs")
    op.drop_index("ix_import_jobs_portfolio_id", table_name="import_jobs")
    op.drop_table("import_jobs")
    op.drop_index("ix_valuation_snapshots_calculated_at", table_name="valuation_snapshots")
    op.drop_index("ix_valuation_snapshots_portfolio_id", table_name="valuation_snapshots")
    op.drop_table("valuation_snapshots")
    op.drop_index("ix_prices_retrieved_at", table_name="prices")
    op.drop_index("ix_prices_quote_currency", table_name="prices")
    op.drop_index("ix_prices_provider", table_name="prices")
    op.drop_index("ix_prices_asset_id", table_name="prices")
    op.drop_table("prices")
    op.drop_index("ix_transactions_occurred_at", table_name="transactions")
    op.drop_index("ix_transactions_kind", table_name="transactions")
    op.drop_index("ix_transactions_asset_id", table_name="transactions")
    op.drop_index("ix_transactions_source_id", table_name="transactions")
    op.drop_table("transactions")
    op.drop_index("ix_balances_asset_id", table_name="balances")
    op.drop_index("ix_balances_source_id", table_name="balances")
    op.drop_table("balances")
    op.drop_index("ix_asset_mappings_provider_asset_id", table_name="asset_mappings")
    op.drop_index("ix_asset_mappings_provider", table_name="asset_mappings")
    op.drop_index("ix_asset_mappings_asset_id", table_name="asset_mappings")
    op.drop_table("asset_mappings")
    op.drop_index("ix_portfolio_sources_kind", table_name="portfolio_sources")
    op.drop_index("ix_portfolio_sources_portfolio_id", table_name="portfolio_sources")
    op.drop_table("portfolio_sources")
    op.drop_index("ix_assets_contract_address", table_name="assets")
    op.drop_index("ix_assets_network_id", table_name="assets")
    op.drop_index("ix_assets_symbol", table_name="assets")
    op.drop_index("ix_assets_canonical_id", table_name="assets")
    op.drop_table("assets")
    op.drop_index("ix_portfolios_user_id", table_name="portfolios")
    op.drop_table("portfolios")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
