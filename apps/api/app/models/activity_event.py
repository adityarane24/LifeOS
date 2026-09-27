from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    JSON,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ActivityEventType(str, Enum):
    """
    Types of events that can occur in LifeOS.
    """

    task_created = "task_created"
    task_updated = "task_updated"
    task_completed = "task_completed"
    task_cancelled = "task_cancelled"
    task_reopened = "task_reopened"

    goal_created = "goal_created"
    goal_updated = "goal_updated"
    goal_completed = "goal_completed"
    goal_progress_updated = "goal_progress_updated"
    goal_cancelled = "goal_cancelled"

    habit_created = "habit_created"
    habit_updated = "habit_updated"
    habit_completed = "habit_completed"
    habit_missed = "habit_missed"
    habit_deactivated = "habit_deactivated"

    project_created = "project_created"
    project_updated = "project_updated"
    project_completed = "project_completed"
    project_archived = "project_archived"

    user_created = "user_created"


class ActivityEntityType(str, Enum):
    """
    Identifies the type of entity associated with an event.
    """

    task = "task"
    goal = "goal"
    habit = "habit"
    project = "project"
    user = "user"


class ActivityEvent(Base):
    """
    Represents an immutable event in the LifeOS activity history.
    """

    __tablename__ = "activity_events"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    event_type: Mapped[ActivityEventType] = mapped_column(
        SqlEnum(ActivityEventType),
        nullable=False,
    )

    entity_type: Mapped[ActivityEntityType] = mapped_column(
        SqlEnum(ActivityEntityType),
        nullable=False,
    )

    entity_id: Mapped[UUID] = mapped_column(
        nullable=False,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    event_metadata: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )