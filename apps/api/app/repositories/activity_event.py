from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.activity_event import ActivityEvent


class ActivityEventRepository:
    """
    Handles database operations for activity events.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        event: ActivityEvent,
    ) -> ActivityEvent:
        """
        Add a new activity event to the database.
        """

        self.db.add(event)
        self.db.flush()

        return event

    def get_by_id(
        self,
        event_id: UUID,
    ) -> ActivityEvent | None:
        """
        Get one activity event by ID.
        """

        return (
            self.db.query(ActivityEvent)
            .filter(ActivityEvent.id == event_id)
            .first()
        )

    def get_by_user(
        self,
        user_id: UUID,
        limit: int = 100,
    ) -> list[ActivityEvent]:
        """
        Get recent activity events for a user.
        """

        return (
            self.db.query(ActivityEvent)
            .filter(ActivityEvent.user_id == user_id)
            .order_by(ActivityEvent.occurred_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        limit: int = 100,
    ) -> list[ActivityEvent]:
        """
        Get activity events for a specific entity.
        """

        return (
            self.db.query(ActivityEvent)
            .filter(
                ActivityEvent.entity_type == entity_type,
                ActivityEvent.entity_id == entity_id,
            )
            .order_by(ActivityEvent.occurred_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self,
        user_id: UUID,
        start: datetime,
        end: datetime,
        limit: int = 100,
    ) -> list[ActivityEvent]:
        """
        Get activity events for a user within a time range.
        """

        return (
            self.db.query(ActivityEvent)
            .filter(
                ActivityEvent.user_id == user_id,
                ActivityEvent.occurred_at >= start,
                ActivityEvent.occurred_at <= end,
            )
            .order_by(ActivityEvent.occurred_at.desc())
            .limit(limit)
            .all()
        )