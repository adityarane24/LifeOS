from uuid import UUID

from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.repositories.goal import GoalRepository
from app.schemas.goal import GoalCreate, GoalUpdate


class GoalService:
    """
    Handles business logic for goals.

    The service sits between the API and repository.
    """

    def __init__(self, db: Session):
        self.repository = GoalRepository(db)
        self.db = db

    def create_goal(self, data: GoalCreate):
        """
        Create a new goal.
        """

        goal = Goal(**data.model_dump())

        self.repository.create(goal)

        self.db.commit()
        self.db.refresh(goal)

        return goal

    def get_goal(self, goal_id: UUID):
        """
        Get one goal by its ID.
        """

        return self.repository.get_by_id(goal_id)

    def get_user_goals(self, user_id: UUID):
        """
        Get all goals belonging to a user.
        """

        return self.repository.get_by_user(user_id)

    def update_goal(self, goal_id: UUID, data: GoalUpdate):
        """
        Update an existing goal.
        """

        goal = self.repository.get_by_id(goal_id)

        if goal is None:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(goal, field, value)

        self.repository.update(goal)

        self.db.commit()
        self.db.refresh(goal)

        return goal

    def delete_goal(self, goal_id: UUID):
        """
        Delete a goal by its ID.
        """

        goal = self.repository.get_by_id(goal_id)

        if goal is None:
            return False

        self.repository.delete(goal)

        self.db.commit()

        return True