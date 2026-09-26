# ---------------------------------------------------------
# Task API Routes
# ---------------------------------------------------------
#
# This file defines the HTTP endpoints for tasks.
#
# Route → Service → Repository → PostgreSQL


from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task import TaskService


# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


# ---------------------------------------------------------
# CREATE TASK
# ---------------------------------------------------------

@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new task.
    """

    service = TaskService(db)

    return service.create_task(data)


# ---------------------------------------------------------
# GET TASKS FOR USER
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[TaskResponse],
)
def get_user_tasks(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Return all tasks belonging to a specific user.
    """

    service = TaskService(db)

    return service.get_user_tasks(user_id)


# ---------------------------------------------------------
# GET SINGLE TASK
# ---------------------------------------------------------

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Return a single task using its ID.
    """

    service = TaskService(db)

    task = service.get_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


# ---------------------------------------------------------
# DELETE TASK
# ---------------------------------------------------------

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a task using its ID.
    """

    service = TaskService(db)

    deleted = service.delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

# ---------------------------------------------------------
# UPDATE TASK
# ---------------------------------------------------------

@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: UUID,
    data: TaskUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing task.

    Only the fields supplied by the client are changed.
    """

    service = TaskService(db)

    task = service.update_task(
        task_id,
        data,
    )

    # If the task doesn't exist, return 404.
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task