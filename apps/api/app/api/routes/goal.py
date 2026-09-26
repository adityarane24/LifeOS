from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from app.services.goal import GoalService


router = APIRouter(
    prefix="/goals",
    tags=["Goals"],
)


@router.post(
    "",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_goal(
    data: GoalCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new goal.
    """

    service = GoalService(db)

    return service.create_goal(data)


@router.get(
    "",
    response_model=list[GoalResponse],
)
def get_user_goals(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get all goals belonging to a user.
    """

    service = GoalService(db)

    return service.get_user_goals(user_id)


@router.get(
    "/{goal_id}",
    response_model=GoalResponse,
)
def get_goal(
    goal_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get one goal by its ID.
    """

    service = GoalService(db)

    goal = service.get_goal(goal_id)

    if goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    return goal


@router.patch(
    "/{goal_id}",
    response_model=GoalResponse,
)
def update_goal(
    goal_id: UUID,
    data: GoalUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing goal.
    """

    service = GoalService(db)

    goal = service.update_goal(goal_id, data)

    if goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    return goal


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_goal(
    goal_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a goal.
    """

    service = GoalService(db)

    deleted = service.delete_goal(goal_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    return None