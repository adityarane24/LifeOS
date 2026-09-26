from datetime import date, datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import (
    ARRAY,
    Boolean,
    Date,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HabitFrequency(str, Enum):
    daily = "daily"
    weekly = "weekly"


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    frequency: Mapped[HabitFrequency] = mapped_column(
        SqlEnum(HabitFrequency),
        default=HabitFrequency.daily,
        nullable=False,
    )

    days_of_week: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    target: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        default="times",
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class HabitCompletion(Base):
    __tablename__ = "habit_completions"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    habit_id: Mapped[UUID] = mapped_column(
        ForeignKey("habits.id"),
        nullable=False,
    )

    completion_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    value: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "habit_id",
            "completion_date",
            name="uq_habit_completion_date",
        ),
    )