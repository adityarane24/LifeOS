# ---------------------------------------------------------
# Habit Service
# ---------------------------------------------------------
#
# This file contains the business logic related to habits.
#
# The service sits between the API routes and the
# repository layer.
#
# Route → Service → Repository → Database


from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEventType,
)
from app.models.habit import Habit, HabitCompletion
from app.repositories.habit import HabitRepository
from app.schemas.habit import (
    HabitCompletionCreate,
    HabitCreate,
    HabitUpdate,
)
from app.services.activity_event import ActivityEventService
from app.services.habit_analytics import HabitAnalytics


class HabitService:
    """
    Contains business logic related to habits.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = HabitRepository(db)
        self.activity_event_service = ActivityEventService(db)

    # -----------------------------
    # Habit Operations
    # -----------------------------

    def create_habit(self, data: HabitCreate) -> Habit:
        """
        Create a new habit.
        """

        habit = Habit(**data.model_dump())

        self.repository.create(habit)

        # Create an activity event for the new habit.
        self.activity_event_service.create_event(
            user_id=habit.user_id,
            event_type=ActivityEventType.habit_created,
            entity_type=ActivityEntityType.habit,
            entity_id=habit.id,
            event_metadata={
                "title": habit.title,
                "frequency": habit.frequency.value,
                "target": habit.target,
                "unit": habit.unit,
            },
        )

        # Commit both the habit and its activity event
        # in the same database transaction.
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

        A normal update creates habit_updated.

        Changing is_active from True to False creates
        habit_deactivated.
        """

        # Find the habit first.
        habit = self.repository.get_by_id(habit_id)

        if habit is None:
            return None

        # Save the old active state before applying updates.
        old_is_active = habit.is_active

        # Get only fields supplied by the client.
        update_data = data.model_dump(
            exclude_unset=True
        )

        # Apply the supplied changes.
        for field, value in update_data.items():
            setattr(habit, field, value)

        self.repository.update(habit)

        # By default, this is a normal habit update.
        event_type = ActivityEventType.habit_updated

        # If the habit was active and is now inactive,
        # record the more specific deactivation event.
        if (
            "is_active" in update_data
            and old_is_active is True
            and habit.is_active is False
        ):
            event_type = ActivityEventType.habit_deactivated

        # Create the activity event.
        self.activity_event_service.create_event(
            user_id=habit.user_id,
            event_type=event_type,
            entity_type=ActivityEntityType.habit,
            entity_id=habit.id,
            event_metadata={
                "updated_fields": list(update_data.keys()),
                "old_is_active": old_is_active,
                "new_is_active": habit.is_active,
            },
        )

        # Commit the habit update and activity event together.
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

        # Find the habit.
        habit = self.repository.get_by_id(habit_id)

        if habit is None:
            raise ValueError("Habit not found")

        # Inactive habits cannot receive new completions.
        if not habit.is_active:
            raise ValueError("Habit is inactive")

        # Check whether a completion already exists
        # for this habit and date.
        existing_completion = self.repository.get_completion(
            habit_id,
            data.completion_date,
        )

        if existing_completion is not None:
            raise ValueError(
                "Habit is already recorded for this date"
            )

        # Create the completion record.
        completion = HabitCompletion(
            habit_id=habit_id,
            completion_date=data.completion_date,
            value=data.value,
            completed=data.completed,
        )

        self.repository.create_completion(completion)

        # Decide which activity event to create.
        if data.completed:
            event_type = ActivityEventType.habit_completed
        else:
            event_type = ActivityEventType.habit_missed

        # Create the activity event.
        #
        # The activity event entity_id points to the habit,
        # because the event represents the user's habit
        # activity rather than exposing the completion record
        # as a separate LifeOS entity.
        self.activity_event_service.create_event(
            user_id=habit.user_id,
            event_type=event_type,
            entity_type=ActivityEntityType.habit,
            entity_id=habit.id,
            event_metadata={
                "completion_date": data.completion_date.isoformat(),
                "value": data.value,
                "completed": data.completed,
            },
        )

        # Commit both the completion and activity event
        # in the same database transaction.
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

    # -----------------------------
    # Habit Analytics
    # -----------------------------

    def get_analytics(
        self,
        habit_id: UUID,
        today: date | None = None,
    ):
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
            today=today,
        )

        longest_streak = HabitAnalytics.calculate_longest_streak(
            habit,
            completions,
        )

        completion_rate = HabitAnalytics.calculate_completion_rate(
            habit,
            completions,
            today=today,
        )

        return {
            "habit_id": habit.id,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "completion_rate": completion_rate,
        }