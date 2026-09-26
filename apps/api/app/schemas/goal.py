from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.goal import GoalPriority, GoalStatus


class GoalCreate(BaseModel):
    user_id: UUID
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: GoalStatus = GoalStatus.pending
    priority: GoalPriority = GoalPriority.medium
    target_date: date | None = None
    progress: int = Field(default=0, ge=0, le=100)


class GoalUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    status: GoalStatus | None = None
    priority: GoalPriority | None = None
    target_date: date | None = None
    progress: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class GoalResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: str | None
    status: GoalStatus
    priority: GoalPriority
    target_date: date | None
    progress: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}