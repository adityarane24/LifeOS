from datetime import datetime, timezone
from uuid import uuid4

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEventType,
)
from app.services.temporal_activity import TemporalActivityService
from app.tests.conftest import TestSessionLocal


def test_get_timeline(test_user):
    """
    Verify that the temporal service returns recent user activity.
    """

    db = TestSessionLocal()

    try:
        service = TemporalActivityService(db)

        service.activity_event_service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_created,
            entity_type=ActivityEntityType.task,
            entity_id=uuid4(),
        )

        service.activity_event_service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.goal_created,
            entity_type=ActivityEntityType.goal,
            entity_id=uuid4(),
        )

        db.commit()

        events = service.get_timeline(test_user.id)

        assert len(events) == 2

        for event in events:
            assert event.user_id == test_user.id

    finally:
        db.close()


def test_get_activity_between(test_user):
    """
    Verify that activity can be retrieved for a specific time range.
    """

    db = TestSessionLocal()

    try:
        service = TemporalActivityService(db)

        event_time = datetime(
            2026,
            9,
            26,
            12,
            0,
            tzinfo=timezone.utc,
        )

        service.activity_event_service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_completed,
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

        events = service.get_activity_between(
            user_id=test_user.id,
            start=start,
            end=end,
        )

        assert len(events) == 1
        assert events[0].event_type == ActivityEventType.task_completed

    finally:
        db.close()


def test_get_entity_history(test_user):
    """
    Verify that the temporal service returns one entity's history.
    """

    db = TestSessionLocal()

    try:
        service = TemporalActivityService(db)

        task_id = uuid4()

        service.activity_event_service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_created,
            entity_type=ActivityEntityType.task,
            entity_id=task_id,
        )

        service.activity_event_service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_completed,
            entity_type=ActivityEntityType.task,
            entity_id=task_id,
        )

        db.commit()

        events = service.get_entity_history(
            entity_type=ActivityEntityType.task,
            entity_id=task_id,
        )

        assert len(events) == 2

        for event in events:
            assert event.entity_id == task_id

    finally:
        db.close()


def test_get_activity_summary(test_user):
    """
    Verify that activity is summarized by event type.
    """

    db = TestSessionLocal()

    try:
        service = TemporalActivityService(db)

        event_time = datetime(
            2026,
            9,
            26,
            12,
            0,
            tzinfo=timezone.utc,
        )

        task_id_1 = uuid4()
        task_id_2 = uuid4()
        goal_id = uuid4()

        service.activity_event_service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_created,
            entity_type=ActivityEntityType.task,
            entity_id=task_id_1,
            occurred_at=event_time,
        )

        service.activity_event_service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_completed,
            entity_type=ActivityEntityType.task,
            entity_id=task_id_1,
            occurred_at=event_time,
        )

        service.activity_event_service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.task_completed,
            entity_type=ActivityEntityType.task,
            entity_id=task_id_2,
            occurred_at=event_time,
        )

        service.activity_event_service.create_event(
            user_id=test_user.id,
            event_type=ActivityEventType.goal_progress_updated,
            entity_type=ActivityEntityType.goal,
            entity_id=goal_id,
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

        summary = service.get_activity_summary(
            user_id=test_user.id,
            start=start,
            end=end,
        )

        assert summary["total_events"] == 4
        assert summary["by_event_type"]["task_created"] == 1
        assert summary["by_event_type"]["task_completed"] == 2
        assert summary["by_event_type"]["goal_progress_updated"] == 1

    finally:
        db.close()


def test_get_activity_summary_returns_empty_summary(test_user):
    """
    Verify that an empty time range returns an empty summary.
    """

    db = TestSessionLocal()

    try:
        service = TemporalActivityService(db)

        start = datetime(
            2026,
            9,
            27,
            0,
            0,
            tzinfo=timezone.utc,
        )

        end = datetime(
            2026,
            9,
            27,
            23,
            59,
            tzinfo=timezone.utc,
        )

        summary = service.get_activity_summary(
            user_id=test_user.id,
            start=start,
            end=end,
        )

        assert summary["total_events"] == 0
        assert summary["by_event_type"] == {}

    finally:
        db.close()
