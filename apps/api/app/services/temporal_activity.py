from collections import Counter
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEvent,
    ActivityEventType,
)
from app.services.activity_event import ActivityEventService


class TemporalActivityService:
    """
    Provides higher-level temporal queries over LifeOS activity events.

    This service does not create activity events.
    ActivityEventService remains responsible for event creation.

    TemporalActivityService is responsible for interpreting
    the event history in useful time-based ways.
    """

    def __init__(self, db: Session):
        self.db = db
        self.activity_event_service = ActivityEventService(db)

    # ---------------------------------------------------------
    # RECENT TIMELINE
    # ---------------------------------------------------------

    def get_timeline(
        self,
        user_id: UUID,
        limit: int = 100,
    ) -> list[ActivityEvent]:
        """
        Return the most recent activity for a user.
        """

        return self.activity_event_service.get_user_events(
            user_id=user_id,
            limit=limit,
        )

    # ---------------------------------------------------------
    # DATE RANGE
    # ---------------------------------------------------------

    def get_activity_between(
        self,
        user_id: UUID,
        start: datetime,
        end: datetime,
        limit: int = 100,
    ) -> list[ActivityEvent]:
        """
        Return activity that occurred between two timestamps.
        """

        return self.activity_event_service.get_events_by_date_range(
            user_id=user_id,
            start=start,
            end=end,
            limit=limit,
        )

    # ---------------------------------------------------------
    # ENTITY HISTORY
    # ---------------------------------------------------------

    def get_entity_history(
        self,
        entity_type: ActivityEntityType,
        entity_id: UUID,
        limit: int = 100,
    ) -> list[ActivityEvent]:
        """
        Return the complete activity history for one entity.

        Example:
            All events belonging to one task.
        """

        return self.activity_event_service.get_entity_events(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
        )

    # ---------------------------------------------------------
    # ACTIVITY SUMMARY
    # ---------------------------------------------------------

    def get_activity_summary(
        self,
        user_id: UUID,
        start: datetime,
        end: datetime,
    ) -> dict:
        """
        Summarize a user's activity within a time range.

        The summary currently counts events by event type.

        Example result:

        {
            "total_events": 10,
            "by_event_type": {
                "task_created": 3,
                "task_completed": 4,
                "habit_completed": 3,
            }
        }
        """

        events = self.activity_event_service.get_events_by_date_range(
            user_id=user_id,
            start=start,
            end=end,
            limit=10000,
        )

        event_counts = Counter(
            event.event_type.value
            for event in events
        )

        return {
            "total_events": len(events),
            "by_event_type": dict(event_counts),
        }
