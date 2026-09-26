from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.project import ProjectPriority, ProjectStatus


class ProjectCreate(BaseModel):
    """
    Data required to create a new project.
    """

    user_id: UUID

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    status: ProjectStatus = ProjectStatus.planned

    priority: ProjectPriority = ProjectPriority.medium

    start_date: date = Field(
        default_factory=date.today,
    )

    target_date: date | None = None


class ProjectUpdate(BaseModel):
    """
    Data that can be changed when updating a project.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    status: ProjectStatus | None = None

    priority: ProjectPriority | None = None

    start_date: date | None = None

    target_date: date | None = None


class ProjectResponse(BaseModel):
    """
    Data returned by the API for a project.
    """

    id: UUID
    user_id: UUID
    title: str
    description: str | None
    status: ProjectStatus
    priority: ProjectPriority
    start_date: date
    target_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }