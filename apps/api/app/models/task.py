# ---------------------------------------------------------
# Task Database Model
# ---------------------------------------------------------
#
# This file defines the Task table used by LifeOS.
#
# SQLAlchemy will use this Python class to describe the
# structure of the "tasks" table in PostgreSQL.


from datetime import datetime

# UUID is Python's built-in UUID type.
from uuid import UUID, uuid4

# Enum allows us to restrict task status and priority
# to predefined values.
from enum import Enum

# SQLAlchemy column types and configuration.
from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, Text, func

# SQLAlchemy ORM tools.
from sqlalchemy.orm import Mapped, mapped_column

# Our common SQLAlchemy Base.
from app.db.base import Base


# ---------------------------------------------------------
# TASK STATUS
# ---------------------------------------------------------

class TaskStatus(str, Enum):
    """
    Possible states of a LifeOS task.
    """

    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


# ---------------------------------------------------------
# TASK PRIORITY
# ---------------------------------------------------------

class TaskPriority(str, Enum):
    """
    Priority levels that can be assigned to a task.
    """

    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


# ---------------------------------------------------------
# TASK MODEL
# ---------------------------------------------------------

class Task(Base):
    """
    Represents a task in LifeOS.

    Each Task object corresponds to one row in the
    PostgreSQL "tasks" table.
    """

    # -----------------------------------------------------
    # TABLE NAME
    # -----------------------------------------------------

    __tablename__ = "tasks"

    # -----------------------------------------------------
    # PRIMARY KEY
    # -----------------------------------------------------
    #
    # Every task needs a unique identifier.

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    # -----------------------------------------------------
    # USER ID / FOREIGN KEY
    # -----------------------------------------------------
    #
    # Every task belongs to a user.
    #
    # ForeignKey connects this column to the primary key
    # of the users table.

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------
    #
    # Short name describing what needs to be done.

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    # -----------------------------------------------------
    # DESCRIPTION
    # -----------------------------------------------------
    #
    # Optional additional information about the task.

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------
    #
    # Defines the current state of the task.

    status: Mapped[TaskStatus] = mapped_column(
        SqlEnum(TaskStatus),
        default=TaskStatus.pending,
        nullable=False,
    )

    # -----------------------------------------------------
    # PRIORITY
    # -----------------------------------------------------
    #
    # Defines how important the task is.

    priority: Mapped[TaskPriority] = mapped_column(
        SqlEnum(TaskPriority),
        default=TaskPriority.medium,
        nullable=False,
    )

    # -----------------------------------------------------
    # DUE DATE
    # -----------------------------------------------------
    #
    # Optional deadline for completing the task.

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # -----------------------------------------------------
    # CREATED AT
    # -----------------------------------------------------
    #
    # PostgreSQL generates the timestamp when the row
    # is created.

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # -----------------------------------------------------
    # UPDATED AT
    # -----------------------------------------------------
    #
    # This records when the row was last modified.

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )