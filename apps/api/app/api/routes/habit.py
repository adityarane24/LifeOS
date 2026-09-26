from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.habit import (
    HabitAnalyticsResponse,
    HabitCompletionCreate,
    HabitCompletionResponse,
    HabitCreate,
    HabitResponse,
    HabitUpdate,
)
from app.services.habit import HabitService


router = APIRouter(
    prefix="/habits",
    tags=["Habits"],
)


# ---------------------------------
# Habit Routes
# ---------------------------------


@router.post(
    "",
    response_model=HabitResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_habit(
    data: HabitCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new habit.
    """

    service = HabitService(db)

    try:
        return service.create_habit(data)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.get(
    "",
    response_model=list[HabitResponse],
)
def get_user_habits(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get all habits belonging to a user.
    """

    service = HabitService(db)

    return service.get_user_habits(user_id)


@router.get(
    "/{habit_id}",
    response_model=HabitResponse,
)
def get_habit(
    habit_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get one habit by ID.
    """

    service = HabitService(db)

    habit = service.get_habit(habit_id)

    if habit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )

    return habit


@router.patch(
    "/{habit_id}",
    response_model=HabitResponse,
)
def update_habit(
    habit_id: UUID,
    data: HabitUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing habit.
    """

    service = HabitService(db)

    habit = service.update_habit(
        habit_id,
        data,
    )

    if habit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )

    return habit


@router.delete(
    "/{habit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_habit(
    habit_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete an existing habit.
    """

    service = HabitService(db)

    deleted = service.delete_habit(habit_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )

    return None


@router.get(
    "/{habit_id}/analytics",
    response_model=HabitAnalyticsResponse,
)
def get_habit_analytics(
    habit_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get calculated analytics for a habit.

    Returns:
    - current streak
    - longest streak
    - completion rate
    """

    service = HabitService(db)

    analytics = service.get_analytics(habit_id)

    if analytics is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found",
        )

    return analytics


# ---------------------------------
# Habit Completion Routes
# ---------------------------------


@router.post(
    "/{habit_id}/completions",
    response_model=HabitCompletionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_completion(
    habit_id: UUID,
    data: HabitCompletionCreate,
    db: Session = Depends(get_db),
):
    """
    Record a habit completion.
    """

    service = HabitService(db)

    try:
        return service.create_completion(
            habit_id,
            data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/{habit_id}/completions",
    response_model=list[HabitCompletionResponse],
)
def get_completions(
    habit_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get completion history for a habit.
    """

    service = HabitService(db)

    try:
        return service.get_completions(habit_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.delete(
    "/{habit_id}/completions/{completion_date}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_completion(
    habit_id: UUID,
    completion_date: date,
    db: Session = Depends(get_db),
):
    """
    Delete a completion for a specific date.
    """

    service = HabitService(db)

    deleted = service.delete_completion(
        habit_id,
        completion_date,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Completion not found",
        )

    return None