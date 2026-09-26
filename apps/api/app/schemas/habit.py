from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.habit import HabitFrequency


class HabitCreate(BaseModel):
    """
    Data required when creating a new habit.
    """

    user_id: UUID

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    frequency: HabitFrequency = HabitFrequency.daily

    days_of_week: list[str] | None = None

    target: int = Field(
        default=1,
        ge=1,
    )

    unit: str = Field(
        default="times",
        min_length=1,
        max_length=50,
    )

    start_date: date = Field(
        default_factory=date.today,
    )

    is_active: bool = True


class HabitUpdate(BaseModel):
    """
    Fields that can be changed when updating a habit.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    frequency: HabitFrequency | None = None

    days_of_week: list[str] | None = None

    target: int | None = Field(
        default=None,
        ge=1,
    )

    unit: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    start_date: date | None = None

    is_active: bool | None = None


class HabitResponse(BaseModel):
    """
    Data returned by the API for a habit.
    """

    id: UUID
    user_id: UUID
    title: str
    description: str | None
    frequency: HabitFrequency
    days_of_week: list[str] | None
    target: int
    unit: str
    start_date: date
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class HabitCompletionCreate(BaseModel):
    """
    Data required to record a habit completion.
    """

    completion_date: date = Field(
        default_factory=date.today,
    )

    value: int = Field(
        default=1,
        ge=0,
    )

    completed: bool = True


class HabitCompletionResponse(BaseModel):
    """
    Data returned by the API for a habit completion.
    """

    id: UUID
    habit_id: UUID
    completion_date: date
    value: int
    completed: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class HabitAnalyticsResponse(BaseModel):
    """
    Calculated statistics for a habit.
    """

    habit_id: UUID
    current_streak: int
    longest_streak: int
    completion_rate: float