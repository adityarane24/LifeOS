from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEventType,
)


class ActivityEventCreate(BaseModel):
    """
    Data required to create an activity event.
    """

    user_id: UUID
    event_type: ActivityEventType
    entity_type: ActivityEntityType
    entity_id: UUID
    event_metadata: dict | None = None
    occurred_at: datetime | None = None


class ActivityEventResponse(BaseModel):
    """
    Data returned when an activity event is read.
    """

    id: UUID
    user_id: UUID
    event_type: ActivityEventType
    entity_type: ActivityEntityType
    entity_id: UUID
    occurred_at: datetime
    event_metadata: dict | None = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }