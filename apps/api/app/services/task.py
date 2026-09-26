# ---------------------------------------------------------
# Task Service
# ---------------------------------------------------------
#
# This file contains the business logic related to tasks.
#
# The service sits between the API routes and the
# repository layer.
#
# Route → Service → Repository → Database


from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """
    Handles business logic for LifeOS tasks.
    """

    def __init__(self, db: Session):
        """
        Create a TaskService using the provided
        database session.
        """

        self.db = db
        self.repository = TaskRepository(db)

    # -----------------------------------------------------
    # CREATE TASK
    # -----------------------------------------------------

    def create_task(self, data: TaskCreate) -> Task:
        """
        Create a new task.

        The task is created using the data validated by
        the Pydantic TaskCreate schema.
        """

        task = Task(
            user_id=data.user_id,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            due_date=data.due_date,
        )

        self.repository.create(task)

        self.db.commit()
        self.db.refresh(task)

        return task

    # -----------------------------------------------------
    # GET TASK
    # -----------------------------------------------------

    def get_task(self, task_id: UUID) -> Task | None:
        """
        Find a task by its ID.
        """

        return self.repository.get_by_id(task_id)

    # -----------------------------------------------------
    # GET USER TASKS
    # -----------------------------------------------------

    def get_user_tasks(self, user_id: UUID) -> list[Task]:
        """
        Return all tasks belonging to a specific user.
        """

        return self.repository.get_by_user(user_id)

    # -----------------------------------------------------
    # DELETE TASK
    # -----------------------------------------------------

    def delete_task(self, task_id: UUID) -> bool:
        """
        Delete a task by its ID.

        Returns:
            True if the task was deleted.
            False if the task did not exist.
        """

        task = self.repository.get_by_id(task_id)

        if task is None:
            return False

        self.repository.delete(task)

        self.db.commit()

        return True


    # -----------------------------------------------------
    # UPDATE TASK
    # -----------------------------------------------------

    def update_task(
        self,
        task_id: UUID,
        data: TaskUpdate,
    ) -> Task | None:
        """
        Update an existing task.

        Only the fields supplied by the client are changed.

        Returns:
            Updated Task if found.
            None if the task does not exist.
        """

        # First find the task.
        task = self.repository.get_by_id(task_id)

        # If the task doesn't exist, return None.
        if task is None:
            return None

        # Convert the Pydantic model into a dictionary
        # containing only fields that were actually supplied.
        update_data = data.model_dump(
            exclude_unset=True
        )

        # Update each supplied field.
        for field, value in update_data.items():
            setattr(task, field, value)

        # Send the changes to the database session.
        self.repository.update(task)

        # Permanently save the changes.
        self.db.commit()

        # Reload the task so we return the latest database
        # values.
        self.db.refresh(task)

        return task
    