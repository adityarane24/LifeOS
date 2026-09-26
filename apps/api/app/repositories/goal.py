from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.goal import Goal


class GoalRepository:
    """
    Handles database operations for Goal objects.

    The repository talks directly to the database.
    It does not contain business rules.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, goal_id: UUID) -> Goal | None:
        """
        Find one goal using its ID.
        """
        statement = select(Goal).where(Goal.id == goal_id)

        return self.db.execute(statement).scalar_one_or_none()

    def get_by_user(self, user_id: UUID) -> list[Goal]:
        """
        Get all goals belonging to a specific user.
        """
        statement = (
            select(Goal)
            .where(Goal.user_id == user_id)
            .order_by(Goal.created_at.desc())
        )

        return list(self.db.execute(statement).scalars().all())

    def create(self, goal: Goal) -> Goal:
        """
        Add a new goal to the current database transaction.
        """
        self.db.add(goal)
        self.db.flush()

        return goal

    def update(self, goal: Goal) -> Goal:
        """
        Flush changes made to an existing goal.
        """
        self.db.flush()

        return goal

    def delete(self, goal: Goal) -> None:
        """
        Delete a goal from the database.
        """
        self.db.delete(goal)
        self.db.flush()