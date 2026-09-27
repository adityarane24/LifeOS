# ---------------------------------------------------------
# ACTIVITY ANALYTICS SERVICE
# ---------------------------------------------------------
#
# This service converts raw LifeOS activity events into
# meaningful personal activity metrics.
#
# Architecture:
#
# Activity Events
#       ↓
# ActivityAnalyticsService
#       ↓
# Analytics metrics
#
# This service does NOT create activity events.
# It only analyzes events that already exist.
# ---------------------------------------------------------

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.activity_event import ActivityEventType
from app.services.temporal_activity import TemporalActivityService


class ActivityAnalyticsService:
    """
    Provides personal activity analytics for LifeOS.

    Analytics are calculated from the immutable activity
    event history.
    """

    def __init__(self, db: Session):
        self.db = db
        self.temporal_activity_service = TemporalActivityService(db)

    # ---------------------------------------------------------
    # USER ANALYTICS
    # ---------------------------------------------------------

    def get_user_analytics(
        self,
        user_id: UUID,
        start: datetime,
        end: datetime,
    ) -> dict:
        """
        Calculate activity analytics for a user
        within a specific time range.

        The current version calculates metrics that can
        be reliably derived from existing activity events.
        """

        events = self.temporal_activity_service.get_activity_between(
            user_id=user_id,
            start=start,
            end=end,
            limit=10000,
        )

        # -----------------------------------------------------
        # EVENT COUNTERS
        # -----------------------------------------------------

        task_created = 0
        task_completed = 0
        task_cancelled = 0
        task_reopened = 0

        goal_completed = 0
        goal_progress_updated = 0

        habit_completed = 0
        habit_missed = 0

        project_completed = 0
        project_archived = 0

        # -----------------------------------------------------
        # PROCESS EVENTS
        # -----------------------------------------------------

        for event in events:

            if event.event_type == ActivityEventType.task_created:
                task_created += 1

            elif event.event_type == ActivityEventType.task_completed:
                task_completed += 1

            elif event.event_type == ActivityEventType.task_cancelled:
                task_cancelled += 1

            elif event.event_type == ActivityEventType.task_reopened:
                task_reopened += 1

            elif event.event_type == ActivityEventType.goal_completed:
                goal_completed += 1

            elif event.event_type == ActivityEventType.goal_progress_updated:
                goal_progress_updated += 1

            elif event.event_type == ActivityEventType.habit_completed:
                habit_completed += 1

            elif event.event_type == ActivityEventType.habit_missed:
                habit_missed += 1

            elif event.event_type == ActivityEventType.project_completed:
                project_completed += 1

            elif event.event_type == ActivityEventType.project_archived:
                project_archived += 1

        # -----------------------------------------------------
        # DERIVED METRICS
        # -----------------------------------------------------

        # Task completion rate is calculated only when
        # at least one task was created.
        #
        # Example:
        #
        # 8 completed / 10 created = 80%
        #
        if task_created > 0:
            task_completion_rate = round(
                (task_completed / task_created) * 100,
                2,
            )
        else:
            task_completion_rate = 0.0

        # Habit consistency is based on completed and
        # missed habit events.
        #
        # Example:
        #
        # 18 completed / (18 + 2 missed) = 90%
        #
        total_habit_outcomes = (
            habit_completed + habit_missed
        )

        if total_habit_outcomes > 0:
            habit_consistency_rate = round(
                (habit_completed / total_habit_outcomes) * 100,
                2,
            )
        else:
            habit_consistency_rate = 0.0

        # -----------------------------------------------------
        # RESULT
        # -----------------------------------------------------

        return {
            "total_events": len(events),

            "tasks": {
                "created": task_created,
                "completed": task_completed,
                "cancelled": task_cancelled,
                "reopened": task_reopened,
                "completion_rate": task_completion_rate,
            },

            "goals": {
                "completed": goal_completed,
                "progress_updates": goal_progress_updated,
            },

            "habits": {
                "completed": habit_completed,
                "missed": habit_missed,
                "consistency_rate": habit_consistency_rate,
            },

            "projects": {
                "completed": project_completed,
                "archived": project_archived,
            },
        }
