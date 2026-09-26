# ---------------------------------------------------------
# Task API Schemas
# ---------------------------------------------------------
#
# This file defines the data structures used by the
# LifeOS Task API.
#
# Pydantic validates data coming from the client and
# controls the data returned by the API.


from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.task import TaskPriority, TaskStatus


# ---------------------------------------------------------
# CREATE TASK REQUEST
# ---------------------------------------------------------

class TaskCreate(BaseModel):
    """
    Data required to create a new task.
    """

    # ID of the user who owns the task.
    user_id: UUID

    # Short name describing the task.
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    # Optional additional information.
    description: str | None = None

    # Initial task status.
    #
    # If the client does not provide a status,
    # the task starts as pending.
    status: TaskStatus = TaskStatus.pending

    # Initial task priority.
    #
    # If the client does not provide a priority,
    # the task starts as medium priority.
    priority: TaskPriority = TaskPriority.medium

    # Optional deadline.
    due_date: datetime | None = None


# ---------------------------------------------------------
# TASK RESPONSE
# ---------------------------------------------------------

class TaskResponse(BaseModel):
    """
    Data returned to the client for a task.
    """

    # Unique task identifier.
    id: UUID

    # User who owns the task.
    user_id: UUID

    # Task title.
    title: str

    # Optional task description.
    description: str | None

    # Current task status.
    status: TaskStatus

    # Current task priority.
    priority: TaskPriority

    # Optional deadline.
    due_date: datetime | None

    # When the task was created.
    created_at: datetime

    # When the task was last modified.
    updated_at: datetime

    # Allows Pydantic to create this schema from a
    # SQLAlchemy Task object.
    model_config = {
        "from_attributes": True
    }

# ---------------------------------------------------------
# UPDATE TASK REQUEST
# ---------------------------------------------------------

class TaskUpdate(BaseModel):
    """
    Data that can be used to update an existing task.

    Every field is optional because a PATCH request should
    allow the client to change only the fields it needs.
    """

    # New task title.
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    # New task description.
    description: str | None = None

    # New task status.
    status: TaskStatus | None = None

    # New task priority.
    priority: TaskPriority | None = None

    # New deadline.
    due_date: datetime | None = None