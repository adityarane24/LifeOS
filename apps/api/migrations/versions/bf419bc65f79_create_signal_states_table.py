"""create signal states table

Revision ID: bf419bc65f79
Revises: 91b1e39f4570
Create Date: 2026-10-17 14:06:26.550162
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bf419bc65f79"
down_revision: Union[str, Sequence[str], None] = "91b1e39f4570"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "signal_states",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("signal_type", sa.String(length=100), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "last_detected_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "signal_type",
            name="uq_signal_states_user_signal",
        ),
    )


def downgrade() -> None:
    op.drop_table("signal_states")