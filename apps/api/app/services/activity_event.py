from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEvent,
    ActivityEventType,
)
from app.repositories.activity_event import ActivityEventRepository


class ActivityEventService:
    """
    Contains business logic for LifeOS activity events.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = ActivityEventRepository(db)

    def create_event(
        self,
        user_id: UUID,
        event_type: ActivityEventType,
        entity_type: ActivityEntityType,
        entity_id: UUID,
        event_metadata: dict | None = None,
        occurred_at: datetime | None = None,
    ) -> ActivityEvent:
        """
        Create a new activity event.

        Events are append-only. Existing events are never updated
        or deleted.
        """

        event = ActivityEvent(
            user_id=user_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            event_metadata=event_metadata,
        )

        if occurred_at is not None:
            event.occurred_at = occurred_at

        self.repository.create(event)

        return event

    def get_event(
        self,
        event_id: UUID,
    ) -> ActivityEvent | None:
        """
        Get one activity event by ID.
        """

        return self.repository.get_by_id(event_id)

    def get_user_events(
        self,
        user_id: UUID,
        limit: int = 100,
    ) -> list[ActivityEvent]:
        """
        Get recent activity events for a user.
        """

        return self.repository.get_by_user(
            user_id,
            limit=limit,
        )

    def get_entity_events(
        self,
        entity_type: ActivityEntityType,
        entity_id: UUID,
        limit: int = 100,
    ) -> list[ActivityEvent]:
        """
        Get activity events for a specific entity.
        """

        return self.repository.get_by_entity(
            entity_type.value,
            entity_id,
            limit=limit,
        )

    def get_events_by_date_range(
        self,
        user_id: UUID,
        start: datetime,
        end: datetime,
        limit: int = 100,
    ) -> list[ActivityEvent]:
        """
        Get activity events for a user within a time range.
        """

        return self.repository.get_by_date_range(
            user_id,
            start,
            end,
            limit=limit,
        )