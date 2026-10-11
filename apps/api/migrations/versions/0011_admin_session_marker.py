"""Distinguish admin-password sessions from regular account sessions."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011_admin_session_marker"
down_revision: str | Sequence[str] | None = "0010_transaction_provenance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("auth_sessions") as batch_op:
        batch_op.add_column(
            sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false())
        )


def downgrade() -> None:
    with op.batch_alter_table("auth_sessions") as batch_op:
        batch_op.drop_column("is_admin")
