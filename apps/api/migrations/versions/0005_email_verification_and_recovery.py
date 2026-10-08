"""Add email verification and one-time password recovery tokens."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_email_verification_recovery"
down_revision: str | Sequence[str] | None = "0004_shared_rate_limits"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email_verified_at", sa.DateTime(timezone=True)))
    op.create_table(
        "auth_action_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auth_action_tokens_user_id", "auth_action_tokens", ["user_id"])
    op.create_index(
        "ix_auth_action_tokens_token_hash", "auth_action_tokens", ["token_hash"], unique=True
    )
    op.create_index("ix_auth_action_tokens_purpose", "auth_action_tokens", ["purpose"])
    op.create_index("ix_auth_action_tokens_expires_at", "auth_action_tokens", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_auth_action_tokens_expires_at", table_name="auth_action_tokens")
    op.drop_index("ix_auth_action_tokens_purpose", table_name="auth_action_tokens")
    op.drop_index("ix_auth_action_tokens_token_hash", table_name="auth_action_tokens")
    op.drop_index("ix_auth_action_tokens_user_id", table_name="auth_action_tokens")
    op.drop_table("auth_action_tokens")
    op.drop_column("users", "email_verified_at")
