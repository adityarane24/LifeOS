# ---------------------------------------------------------
# Goal Service
# ---------------------------------------------------------
#
# This file contains the business logic related to goals.
#
# The service sits between the API routes and the
# repository layer.
#
# Route → Service → Repository → Database


from uuid import UUID

from sqlalchemy.orm import Session

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEventType,
)
from app.models.goal import Goal, GoalStatus
from app.repositories.goal import GoalRepository
from app.schemas.goal import GoalCreate, GoalUpdate
from app.services.activity_event import ActivityEventService


class GoalService:
    """
    Handles business logic for goals.
    """

    def __init__(self, db: Session):
        """
        Create a GoalService using the provided
        database session.
        """

        self.db = db
        self.repository = GoalRepository(db)
        self.activity_event_service = ActivityEventService(db)

    # -----------------------------------------------------
    # CREATE GOAL
    # -----------------------------------------------------

    def create_goal(self, data: GoalCreate):
        """
        Create a new goal.

        The goal is created using the data validated by
        the Pydantic GoalCreate schema.
        """

        goal = Goal(**data.model_dump())

        self.repository.create(goal)

        # Create an activity event for the new goal.
        self.activity_event_service.create_event(
            user_id=goal.user_id,
            event_type=ActivityEventType.goal_created,
            entity_type=ActivityEntityType.goal,
            entity_id=goal.id,
            event_metadata={
                "title": goal.title,
                "priority": goal.priority.value,
            },
        )

        # Commit both the goal and its activity event
        # in the same database transaction.
        self.db.commit()

        # Reload the goal with the latest database values.
        self.db.refresh(goal)

        return goal

    # -----------------------------------------------------
    # GET GOAL
    # -----------------------------------------------------

    def get_goal(self, goal_id: UUID):
        """
        Get one goal by its ID.
        """

        return self.repository.get_by_id(goal_id)

    # -----------------------------------------------------
    # GET USER GOALS
    # -----------------------------------------------------

    def get_user_goals(self, user_id: UUID):
        """
        Get all goals belonging to a user.
        """

        return self.repository.get_by_user(user_id)

    # -----------------------------------------------------
    # UPDATE GOAL
    # -----------------------------------------------------

    def update_goal(
        self,
        goal_id: UUID,
        data: GoalUpdate,
    ):
        """
        Update an existing goal.

        Only the fields supplied by the client are changed.

        Special activity events are created when the goal
        progresses or changes lifecycle state.
        """

        # First find the goal.
        goal = self.repository.get_by_id(goal_id)

        # If the goal doesn't exist, return None.
        if goal is None:
            return None

        # Save the old values before applying updates.
        #
        # These are needed to determine whether the update
        # represents progress or a status transition.
        old_status = goal.status
        old_progress = goal.progress

        # Convert the Pydantic model into a dictionary
        # containing only fields that were actually supplied.
        update_data = data.model_dump(
            exclude_unset=True
        )

        # Update each supplied field.
        for field, value in update_data.items():
            setattr(goal, field, value)

        # Send the changes to the database session.
        self.repository.update(goal)

        # -------------------------------------------------
        # ACTIVITY EVENT
        # -------------------------------------------------
        #
        # Normal goal changes create goal_updated.
        #
        # Progress changes create goal_progress_updated.
        #
        # Completing a goal creates goal_completed.
        #
        # Cancelling a goal creates goal_cancelled.

        event_type = ActivityEventType.goal_updated

        # First check for important status transitions.
        if "status" in update_data:

            new_status = goal.status

            # Goal was completed.
            if new_status == GoalStatus.completed:
                event_type = ActivityEventType.goal_completed

            # Goal was cancelled.
            elif new_status == GoalStatus.cancelled:
                event_type = ActivityEventType.goal_cancelled

        # If the status did not produce a special lifecycle
        # event, check whether the progress changed.
        elif "progress" in update_data:
            event_type = ActivityEventType.goal_progress_updated

        # Create the activity event.
        self.activity_event_service.create_event(
            user_id=goal.user_id,
            event_type=event_type,
            entity_type=ActivityEntityType.goal,
            entity_id=goal.id,
            event_metadata={
                "updated_fields": list(update_data.keys()),
                "old_status": old_status.value,
                "new_status": goal.status.value,
                "old_progress": old_progress,
                "new_progress": goal.progress,
            },
        )

        # Commit both the goal update and the activity event
        # in the same database transaction.
        self.db.commit()

        # Reload the goal so we return the latest database
        # values.
        self.db.refresh(goal)

        return goal

    # -----------------------------------------------------
    # DELETE GOAL
    # -----------------------------------------------------

    def delete_goal(self, goal_id: UUID):
        """
        Delete a goal by its ID.

        Returns:
            True if the goal was deleted.
            False if the goal did not exist.
        """

        goal = self.repository.get_by_id(goal_id)

        if goal is None:
            return False

        self.repository.delete(goal)

        self.db.commit()

        return True