from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (Boolean, DateTime, ForeignKey, String, UniqueConstraint, func)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SignalState(Base):
    __tablename__ = "signal_states"

    __table_args__ = (
    UniqueConstraint(
        "user_id",
        "signal_type",
        name="uq_signal_states_user_signal",
    ),
)

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    signal_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    last_detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )