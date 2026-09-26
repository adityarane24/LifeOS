# ---------------------------------------------------------
# Task Repository
# ---------------------------------------------------------
#
# This file contains database operations related to tasks.
#
# The repository is responsible only for communicating
# with the database.
#
# Business logic belongs in the service layer.


from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task


class TaskRepository:
    """
    Handles database operations for Task objects.
    """

    def __init__(self, db: Session):
        """
        Store the database session that will be used
        by this repository.
        """

        self.db = db

    # -----------------------------------------------------
    # GET TASK BY ID
    # -----------------------------------------------------

    def get_by_id(self, task_id: UUID) -> Task | None:
        """
        Find a task using its ID.

        Returns:
            Task object if found.
            None if the task does not exist.
        """

        statement = select(Task).where(Task.id == task_id)

        return self.db.execute(statement).scalar_one_or_none()

    # -----------------------------------------------------
    # GET TASKS FOR USER
    # -----------------------------------------------------

    def get_by_user(self, user_id: UUID) -> list[Task]:
        """
        Return all tasks belonging to a specific user.
        """

        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )

        return list(self.db.execute(statement).scalars().all())

    # -----------------------------------------------------
    # CREATE TASK
    # -----------------------------------------------------

    def create(self, task: Task) -> Task:
        """
        Add a new task to the database session.

        The service layer will handle committing
        the transaction.
        """

        self.db.add(task)
        self.db.flush()

        return task

    # -----------------------------------------------------
    # DELETE TASK
    # -----------------------------------------------------

    def delete(self, task: Task) -> None:
        """
        Delete a task from the database session.

        The service layer will handle committing
        the transaction.
        """

        self.db.delete(task)
        self.db.flush()

    # -----------------------------------------------------
    # UPDATE TASK
    # -----------------------------------------------------

    def update(self, task: Task) -> Task:
        """
        Mark the task as modified in the database session.

        The service layer will make the actual field changes
        and handle the transaction.
        """

        self.db.flush()

        return task