from datetime import datetime, timezone
from uuid import uuid4

from app.models.activity_event import (
    ActivityEntityType,
    ActivityEvent,
    ActivityEventType,
)
from app.services.activity_analytics import ActivityAnalyticsService
from app.tests.conftest import TestSessionLocal


def test_user_analytics(test_user):
    """
    Verify that analytics correctly count activity events
    and calculate derived metrics.
    """

    db = TestSessionLocal()

    try:
        event_time = datetime(
            2026,
            9,
            26,
            12,
            0,
            tzinfo=timezone.utc,
        )

        events = [
            # Tasks
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.task_created,
                entity_type=ActivityEntityType.task,
                entity_id=uuid4(),
                occurred_at=event_time,
            ),
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.task_created,
                entity_type=ActivityEntityType.task,
                entity_id=uuid4(),
                occurred_at=event_time,
            ),
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.task_completed,
                entity_type=ActivityEntityType.task,
                entity_id=uuid4(),
                occurred_at=event_time,
            ),
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.task_cancelled,
                entity_type=ActivityEntityType.task,
                entity_id=uuid4(),
                occurred_at=event_time,
            ),
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.task_reopened,
                entity_type=ActivityEntityType.task,
                entity_id=uuid4(),
                occurred_at=event_time,
            ),

            # Goals
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.goal_completed,
                entity_type=ActivityEntityType.goal,
                entity_id=uuid4(),
                occurred_at=event_time,
            ),
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.goal_progress_updated,
                entity_type=ActivityEntityType.goal,
                entity_id=uuid4(),
                occurred_at=event_time,
            ),
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.goal_progress_updated,
                entity_type=ActivityEntityType.goal,
                entity_id=uuid4(),
                occurred_at=event_time,
            ),

            # Habits
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.habit_completed,
                entity_type=ActivityEntityType.habit,
                entity_id=uuid4(),
                occurred_at=event_time,
            ),
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.habit_completed,
                entity_type=ActivityEntityType.habit,
                entity_id=uuid4(),
                occurred_at=event_time,
            ),
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.habit_missed,
                entity_type=ActivityEntityType.habit,
                entity_id=uuid4(),
                occurred_at=event_time,
            ),

            # Projects
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.project_completed,
                entity_type=ActivityEntityType.project,
                entity_id=uuid4(),
                occurred_at=event_time,
            ),
            ActivityEvent(
                user_id=test_user.id,
                event_type=ActivityEventType.project_archived,
                entity_type=ActivityEntityType.project,
                entity_id=uuid4(),
                occurred_at=event_time,
            ),
        ]

        db.add_all(events)
        db.commit()

        service = ActivityAnalyticsService(db)

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

        analytics = service.get_user_analytics(
            user_id=test_user.id,
            start=start,
            end=end,
        )

        # Total events
        assert analytics["total_events"] == 13

        # Tasks
        assert analytics["tasks"]["created"] == 2
        assert analytics["tasks"]["completed"] == 1
        assert analytics["tasks"]["cancelled"] == 1
        assert analytics["tasks"]["reopened"] == 1

        # 1 completed / 2 created = 50%
        assert analytics["tasks"]["completion_rate"] == 50.0

        # Goals
        assert analytics["goals"]["completed"] == 1
        assert analytics["goals"]["progress_updates"] == 2

        # Habits
        assert analytics["habits"]["completed"] == 2
        assert analytics["habits"]["missed"] == 1

        # 2 completed / (2 completed + 1 missed) = 66.67%
        assert analytics["habits"]["consistency_rate"] == 66.67

        # Projects
        assert analytics["projects"]["completed"] == 1
        assert analytics["projects"]["archived"] == 1

    finally:
        db.close()


def test_user_analytics_empty_range(test_user):
    """
    Verify that analytics return zero values when
    there is no activity in the requested period.
    """

    db = TestSessionLocal()

    try:
        service = ActivityAnalyticsService(db)

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

        analytics = service.get_user_analytics(
            user_id=test_user.id,
            start=start,
            end=end,
        )

        assert analytics["total_events"] == 0

        assert analytics["tasks"]["created"] == 0
        assert analytics["tasks"]["completed"] == 0
        assert analytics["tasks"]["completion_rate"] == 0.0

        assert analytics["goals"]["completed"] == 0
        assert analytics["goals"]["progress_updates"] == 0

        assert analytics["habits"]["completed"] == 0
        assert analytics["habits"]["missed"] == 0
        assert analytics["habits"]["consistency_rate"] == 0.0

        assert analytics["projects"]["completed"] == 0
        assert analytics["projects"]["archived"] == 0

    finally:
        db.close()
