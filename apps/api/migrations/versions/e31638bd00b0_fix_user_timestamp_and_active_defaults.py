"""fix user timestamp and active defaults

Revision ID: e31638bd00b0
Revises: dc64628314c3
Create Date: 2026-09-01 20:06:33.412445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e31638bd00b0'
down_revision: Union[str, Sequence[str], None] = 'dc64628314c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix users table defaults and timestamp types."""

    # -----------------------------------------------------
    # FIX CREATED_AT
    # -----------------------------------------------------
    #
    # Change:
    #
    # timestamp without time zone
    #
    # into:
    #
    # timestamp with time zone
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )

    # -----------------------------------------------------
    # FIX UPDATED_AT
    # -----------------------------------------------------
    #
    # Make updated_at timezone-aware as well.
    op.alter_column(
        "users",
        "updated_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )

    # -----------------------------------------------------
    # FIX IS_ACTIVE DEFAULT
    # -----------------------------------------------------
    #
    # PostgreSQL should automatically use TRUE when
    # is_active isn't explicitly provided.
    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.Boolean(),
        existing_nullable=False,
        server_default=sa.true(),
    )


def downgrade() -> None:
    """Revert the users table corrections."""

    # Remove the PostgreSQL-side default from is_active.
    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.Boolean(),
        existing_nullable=False,
        server_default=None,
    )

    # Change created_at back to a timestamp without timezone.
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )

    # Change updated_at back to a timestamp without timezone.
    op.alter_column(
        "users",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )