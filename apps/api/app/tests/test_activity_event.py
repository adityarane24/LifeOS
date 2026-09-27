from datetime import datetime, timezone
from uuid import uuid4

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEventType,
)
from app.tests.conftest import TestSessionLocal
from app.services.activity_event import ActivityEventService


def test_create_activity_event(test_user):
    """
    Verify that an activity event can be created.
    """

    db = TestSessionLocal()

    try:
        service = ActivityEventService(db)

        entity_id = uuid4()

        event = service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_created,
            entity_type=ActivityEntityType.task,
            entity_id=entity_id,
            event_metadata={
                "title": "Test task",
            },
        )

        db.commit()
        db.refresh(event)

        assert event.id is not None
        assert event.user_id == test_user.id
        assert event.event_type == ActivityEventType.task_created
        assert event.entity_type == ActivityEntityType.task
        assert event.entity_id == entity_id
        assert event.event_metadata == {
            "title": "Test task",
        }

    finally:
        db.close()


def test_create_activity_event_with_timestamp(test_user):
    """
    Verify that a custom event timestamp can be stored.
    """

    db = TestSessionLocal()

    try:
        service = ActivityEventService(db)

        entity_id = uuid4()

        occurred_at = datetime(
            2026,
            9,
            26,
            18,
            30,
            tzinfo=timezone.utc,
        )

        event = service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.goal_progress_updated,
            entity_type=ActivityEntityType.goal,
            entity_id=entity_id,
            event_metadata={
                "previous_progress": 40,
                "new_progress": 60,
            },
            occurred_at=occurred_at,
        )

        db.commit()
        db.refresh(event)

        assert event.occurred_at == occurred_at
        assert event.event_metadata["previous_progress"] == 40
        assert event.event_metadata["new_progress"] == 60

    finally:
        db.close()


def test_get_user_events(test_user):
    """
    Verify that events can be retrieved for a user.
    """

    db = TestSessionLocal()

    try:
        service = ActivityEventService(db)

        first_entity_id = uuid4()
        second_entity_id = uuid4()

        service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_created,
            entity_type=ActivityEntityType.task,
            entity_id=first_entity_id,
        )

        service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_completed,
            entity_type=ActivityEntityType.task,
            entity_id=second_entity_id,
        )

        db.commit()

        events = service.get_user_events(
            test_user.id
        )

        assert len(events) == 2

        for event in events:
            assert event.user_id == test_user.id

    finally:
        db.close()


def test_get_entity_events(test_user):
    """
    Verify that events can be retrieved for one entity.
    """

    db = TestSessionLocal()

    try:
        service = ActivityEventService(db)

        task_id = uuid4()
        other_task_id = uuid4()

        service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_created,
            entity_type=ActivityEntityType.task,
            entity_id=task_id,
        )

        service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_completed,
            entity_type=ActivityEntityType.task,
            entity_id=task_id,
        )

        service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_created,
            entity_type=ActivityEntityType.task,
            entity_id=other_task_id,
        )

        db.commit()

        events = service.get_entity_events(
            ActivityEntityType.task,
            task_id,
        )

        assert len(events) == 2

        for event in events:
            assert event.entity_id == task_id

    finally:
        db.close()


def test_get_event(test_user):
    """
    Verify that one activity event can be retrieved by ID.
    """

    db = TestSessionLocal()

    try:
        service = ActivityEventService(db)

        event = service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_completed,
            entity_type=ActivityEntityType.task,
            entity_id=uuid4(),
        )

        db.commit()

        stored_event = service.get_event(event.id)

        assert stored_event is not None
        assert stored_event.id == event.id
        assert stored_event.user_id == test_user.id

    finally:
        db.close()


def test_get_events_by_date_range(test_user):
    """
    Verify that events can be retrieved within a date range.
    """

    db = TestSessionLocal()

    try:
        service = ActivityEventService(db)

        event_time = datetime(
            2026,
            9,
            26,
            12,
            0,
            tzinfo=timezone.utc,
        )

        service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_created,
            entity_type=ActivityEntityType.task,
            entity_id=uuid4(),
            occurred_at=event_time,
        )

        db.commit()

        start = datetime(
            2026,
            9,
            26,
            0,
            0,
            tzinfo=timezone.utc,
        )

        end = datetime(
            2026,
            9,
            26,
            23,
            59,
            tzinfo=timezone.utc,
        )

        events = service.get_events_by_date_range(
            test_user.id,
            start,
            end,
        )

        assert len(events) == 1
        assert events[0].user_id == test_user.id

    finally:
        db.close()