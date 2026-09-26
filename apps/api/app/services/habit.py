from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.habit import Habit, HabitCompletion
from app.repositories.habit import HabitRepository
from app.services.habit_analytics import HabitAnalytics
from app.schemas.habit import (
    HabitCompletionCreate,
    HabitCreate,
    HabitUpdate,
)


class HabitService:
    """
    Contains business logic related to habits.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = HabitRepository(db)

    # -----------------------------
    # Habit Operations
    # -----------------------------

    def create_habit(self, data: HabitCreate) -> Habit:
        """
        Create a new habit.
        """

        habit = Habit(**data.model_dump())

        self.repository.create(habit)

        self.db.commit()
        self.db.refresh(habit)

        return habit

    def get_habit(self, habit_id: UUID) -> Habit | None:
        """
        Get one habit by ID.
        """

        return self.repository.get_by_id(habit_id)

    def get_user_habits(self, user_id: UUID) -> list[Habit]:
        """
        Get all habits belonging to a user.
        """

        return self.repository.get_by_user(user_id)

    def update_habit(
        self,
        habit_id: UUID,
        data: HabitUpdate,
    ) -> Habit | None:
        """
        Update an existing habit.
        """

        habit = self.repository.get_by_id(habit_id)

        if habit is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(habit, field, value)

        self.repository.update(habit)

        self.db.commit()
        self.db.refresh(habit)

        return habit

    def delete_habit(self, habit_id: UUID) -> bool:
        """
        Delete an existing habit.
        """

        habit = self.repository.get_by_id(habit_id)

        if habit is None:
            return False

        self.repository.delete(habit)

        self.db.commit()

        return True

    # -----------------------------
    # Habit Completion Operations
    # -----------------------------

    def create_completion(
        self,
        habit_id: UUID,
        data: HabitCompletionCreate,
    ) -> HabitCompletion:
        """
        Record a completion for a habit.
        """

        habit = self.repository.get_by_id(habit_id)

        if habit is None:
            raise ValueError("Habit not found")

        if not habit.is_active:
            raise ValueError("Habit is inactive")

        existing_completion = self.repository.get_completion(
            habit_id,
            data.completion_date,
        )

        if existing_completion is not None:
            raise ValueError(
                "Habit is already recorded for this date"
            )

        completion = HabitCompletion(
            habit_id=habit_id,
            completion_date=data.completion_date,
            value=data.value,
            completed=data.completed,
        )

        self.repository.create_completion(completion)

        self.db.commit()
        self.db.refresh(completion)

        return completion

    def get_completions(
        self,
        habit_id: UUID,
    ) -> list[HabitCompletion]:
        """
        Get all completion records for a habit.
        """

        habit = self.repository.get_by_id(habit_id)

        if habit is None:
            raise ValueError("Habit not found")

        return self.repository.get_completions(habit_id)

    def delete_completion(
        self,
        habit_id: UUID,
        completion_date: date,
    ) -> bool:
        """
        Delete a completion for a specific date.
        """

        completion = self.repository.get_completion(
            habit_id,
            completion_date,
        )

        if completion is None:
            return False

        self.repository.delete_completion(completion)

        self.db.commit()

        return True



    def get_analytics(self, habit_id: UUID):
        """
        Calculate analytics for a habit.
        """

        habit = self.repository.get_by_id(habit_id)

        if habit is None:
            return None

        completions = self.repository.get_completions(
            habit_id
        )

        current_streak = HabitAnalytics.calculate_current_streak(
            habit,
            completions,
        )

        longest_streak = HabitAnalytics.calculate_longest_streak(
            habit,
            completions,
        )

        completion_rate = HabitAnalytics.calculate_completion_rate(
            habit,
            completions,
        )

        return {
            "habit_id": habit.id,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "completion_rate": completion_rate,
        }