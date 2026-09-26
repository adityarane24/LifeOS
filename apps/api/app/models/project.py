from datetime import date, datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import (
    Date,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProjectStatus(str, Enum):
    planned = "planned"
    active = "active"
    completed = "completed"
    archived = "archived"


class ProjectPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Project(Base):
    """
    Database model representing a LifeOS project.

    A project is a collection of related work that helps
    the user achieve a larger outcome.
    """

    __tablename__ = "projects"

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

    status: Mapped[ProjectStatus] = mapped_column(
        SqlEnum(ProjectStatus),
        default=ProjectStatus.planned,
        nullable=False,
    )

    priority: Mapped[ProjectPriority] = mapped_column(
        SqlEnum(ProjectPriority),
        default=ProjectPriority.medium,
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False,
    )

    target_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
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