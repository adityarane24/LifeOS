from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.habit import Habit, HabitCompletion


class HabitRepository:
    """
    Handles database operations related to habits.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, habit_id: UUID) -> Habit | None:
        """
        Find one habit using its ID.
        """

        statement = select(Habit).where(
            Habit.id == habit_id
        )

        return self.db.execute(statement).scalar_one_or_none()

    def get_by_user(self, user_id: UUID) -> list[Habit]:
        """
        Get all habits belonging to a user.
        """

        statement = (
            select(Habit)
            .where(Habit.user_id == user_id)
            .order_by(Habit.created_at.desc())
        )

        return list(
            self.db.execute(statement)
            .scalars()
            .all()
        )

    def create(self, habit: Habit) -> Habit:
        """
        Add a new habit to the database session.
        """

        self.db.add(habit)
        self.db.flush()

        return habit

    def update(self, habit: Habit) -> Habit:
        """
        Save changes made to an existing habit.
        """

        self.db.flush()

        return habit

    def delete(self, habit: Habit) -> None:
        """
        Delete a habit.
        """

        self.db.delete(habit)
        self.db.flush()

    # -----------------------------
    # Habit Completion Operations
    # -----------------------------

    def get_completion(
        self,
        habit_id: UUID,
        completion_date: date,
    ) -> HabitCompletion | None:
        """
        Find a completion record for a habit on a specific date.
        """

        statement = select(HabitCompletion).where(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.completion_date == completion_date,
        )

        return self.db.execute(statement).scalar_one_or_none()

    def get_completions(
        self,
        habit_id: UUID,
    ) -> list[HabitCompletion]:
        """
        Get all completion records for a habit.
        """

        statement = (
            select(HabitCompletion)
            .where(HabitCompletion.habit_id == habit_id)
            .order_by(HabitCompletion.completion_date.desc())
        )

        return list(
            self.db.execute(statement)
            .scalars()
            .all()
        )

    def create_completion(
        self,
        completion: HabitCompletion,
    ) -> HabitCompletion:
        """
        Add a habit completion record.
        """

        self.db.add(completion)
        self.db.flush()

        return completion

    def delete_completion(
        self,
        completion: HabitCompletion,
    ) -> None:
        """
        Delete a habit completion record.
        """

        self.db.delete(completion)
        self.db.flush()